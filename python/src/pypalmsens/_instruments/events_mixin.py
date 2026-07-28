from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from System.Threading.Tasks import Task
from typing_extensions import override

from ..types import AllowedEvents
from .callback import Status

if TYPE_CHECKING:
    from ..data import Curve, EISData, Measurement
    from .callback import CallbackData, CallbackDataEIS


@dataclass
class EventHandle:
    emitter: EventsMixin
    event: AllowedEvents
    callback: Callable[..., None]

    def cancel(self) -> None:
        self.emitter._listeners[self.event].remove(self.callback)


@dataclass
class EventHandleReceiveMessage(EventHandle):
    _loop: asyncio.AbstractEventLoop | None = None

    def __post_init__(self):
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            handler = self._receive_message_handler
        else:
            handler = self._receive_message_handler_async

        self.emitter._comm.ClientConnection.ReceiveMessage += handler

    def _receive_message_handler(self, sender, message: str) -> None:
        """Message handler helper function to schedule the callback."""
        self.callback(message)

    def _receive_message_handler_async(self, sender, message: str) -> None:
        """Async message handler helper function to schedule the callback."""
        assert self._loop
        _ = self._loop.call_soon_threadsafe(self.callback, message)
        return Task.CompletedTask

    @override
    def cancel(self):
        if self._loop:
            self.emitter._comm.ClientConnection.ReceiveMessage -= (
                self._receive_message_handler_async
            )
        else:
            self.emitter._comm.ClientConnection.ReceiveMessage -= self._receive_message_handler


@dataclass
class EventHandleStatus(EventHandle):
    _loop: asyncio.AbstractEventLoop | None = None

    def __post_init__(self):
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self.emitter._comm.ClientConnection.ReceiveStatus += self._idle_status_handler
        else:
            self.emitter._comm.ClientConnection.ReceiveStatusAsync += (
                self._idle_status_handler_async
            )

    def _idle_status_handler(self, sender, args) -> None:
        """Message handler helper function to schedule the callback."""
        status = Status._from_event_args(args)

        self.callback(status)

    def _idle_status_handler_async(self, sender, args) -> None:
        """Async message handler helper function to schedule the callback."""
        status = Status._from_event_args(args)

        assert self._loop
        _ = self._loop.call_soon_threadsafe(self.callback, status)
        return Task.CompletedTask

    @override
    def cancel(self):
        if self._loop:
            self.emitter._comm.ClientConnection.ReceiveStatusAsync -= (
                self._idle_status_handler_async
            )
        else:
            self.emitter._comm.ClientConnection.ReceiveStatus -= self._idle_status_handler


class EventsMixin:
    def __init__(self):
        self._listeners: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def on(
        self,
        event: AllowedEvents,
        callback: Callable[..., None],
    ) -> EventHandle:
        """Add callback to event."""
        if event == 'receive_message':
            return EventHandleReceiveMessage(emitter=self, event=event, callback=callback)

        elif event == 'receive_status':
            return EventHandleStatus(emitter=self, event=event, callback=callback)

        self._listeners[event].append(callback)
        return EventHandle(emitter=self, event=event, callback=callback)

    def on_error(self, callback: Callable[..., None]) -> EventHandle:
        """Called when a connection or communication error occurs."""
        return self.on('error', callback=callback)

    def on_measurement_begin(self, callback: Callable[[Measurement], None]) -> EventHandle:
        """Called at the start of a measurement."""
        return self.on('measurement_begin', callback=callback)

    def on_measurement_end(self, callback: Callable[..., None]) -> EventHandle:
        """Called at the end of a measurement."""
        return self.on('measurement_end', callback=callback)

    def on_curve_begin(self, callback: Callable[[Curve], None]) -> EventHandle:
        """Called at the start of a new curve (for EIS use on_eis_data_start)."""
        return self.on('curve_begin', callback=callback)

    def on_curve_new_data(self, callback: Callable[[CallbackData], None]) -> EventHandle:
        """Called when new data are received (for EIS use on_eis_new_data).

        Note that the data are batched depending on available resources."""
        return self.on('curve_new_data', callback=callback)

    def on_curve_end(self, callback: Callable[[Curve], None]) -> EventHandle:
        """Called at the end of a curve (for EIS use on_eis_data_end)."""
        return self.on('curve_end', callback=callback)

    def on_eis_data_begin(self, callback: Callable[[EISData], None]) -> EventHandle:
        """Called at the start of a new EIS data set."""
        return self.on('eis_data_begin', callback=callback)

    def on_eis_new_data(self, callback: Callable[[CallbackDataEIS], None]) -> EventHandle:
        """Called when new eis data are received.

        Data points are batched depending on available resources."""
        return self.on('eis_new_data', callback=callback)

    def on_eis_data_end(self, callback: Callable[..., None]) -> EventHandle:
        """Called at the end of an EIS data set."""
        return self.on('eis_data_end', callback=callback)

    def on_measurement_setup(self, callback: Callable[..., None]) -> EventHandle:
        """
        Called before the measurement starts.

        Use this to set up file resources, database connections, etc."""
        return self.on('measurement_setup', callback=callback)

    def on_measurement_teardown(self, callback: Callable[..., None]) -> EventHandle:
        """Called after the measurement has ended, either succesfully or after an error occurs.

        Use this to close files or clean up resources."""
        return self.on('measurement_teardown', callback=callback)

    def on_receive_message(self, callback: Callable[[str], None], /):
        """Register callback when a message is received.

        The callback is triggered, for example, when a method is started,
        or when `send_string` is called in MethodSCRIPT.

        Parameters
        ----------
        callback: Callable[[str], None]
            The function to call when triggered
        """
        return self.on('receive_message', callback=callback)

    def on_receive_status(self, callback: Callable[[Status], None], /):
        """Register callback for idle status events.

        The callback is triggered when the current/potential are updated
        durinig idle state or pretreatment phases.

        Parameters
        ----------
        callback: Callable[[Status], None]
            The function to call when triggered
        """
        return self.on('receive_status', callback=callback)
