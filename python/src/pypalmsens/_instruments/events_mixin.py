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
        """Remove this callback from the emitter's listeners."""
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
        except RuntimeError as exc:
            raise RuntimeError("'receive_message' requires active event loop.") from exc
        else:
            self.emitter._comm.ClientConnection.ReceiveStatusAsync += (
                self._idle_status_handler_async
            )

        _ = self._loop.call_soon_threadsafe(self.emitter._comm.SetStatusWhenIdleAsync, True)

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
        self.emitter._comm.ClientConnection.ReceiveStatusAsync -= (
            self._idle_status_handler_async
        )

        assert self._loop
        _ = self._loop.call_soon_threadsafe(self.emitter._comm.SetStatusWhenIdleAsync, False)


class EventsMixin:
    def __init__(self):
        self._listeners: dict[AllowedEvents, list[Callable[..., None]]] = defaultdict(list)

    def on(
        self,
        event: AllowedEvents,
        callback: Callable[..., None],
    ) -> EventHandle:
        """Register a callback to invoke for the specified event.

        Parameters
        ----------
        event : AllowedEvents
            Name of the event to subscribe to. For most events this simply
            appends callback to the internal listeners dictionary.
        callback : Callable[..., None]
            Function that will be invoked when the event is triggered.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.

        Notes
        -----
        * ``'receive_message'`` and ``'receive_status'`` are handled specially:
          they create instances of :class:`EventHandleReceiveMessage` or
          :class:`EventHandleStatus`, respectively, which attach the callback
          directly to the underlying communication layer.
        """
        if event == 'receive_message':
            return EventHandleReceiveMessage(emitter=self, event=event, callback=callback)

        elif event == 'receive_status':
            return EventHandleStatus(emitter=self, event=event, callback=callback)

        self._listeners[event].append(callback)
        return EventHandle(emitter=self, event=event, callback=callback)

    def on_error(self, callback: Callable[..., None]) -> EventHandle:
        """Register a callback to invoke when an error occurs during a measurement.

        These errors can be a connection or communication error.

        Parameters
        ----------
        callback : Callable
            The function to call when triggered.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('error', callback=callback)

    def on_measurement_begin(self, callback: Callable[[Measurement], None]) -> EventHandle:
        """Register a callback to invoke at the start of a measurement.

        Parameters
        ----------
        callback : Callable
            The function to call when triggered.
            Passes [pypalmsens.data.Measurement][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('measurement_begin', callback=callback)

    def on_measurement_end(self, callback: Callable[[Measurement], None]) -> EventHandle:
        """Register a callback to invoke at the end of a measurement.

        Parameters
        ----------
        callback : Callable
            The function to call when triggered.
            Passes [pypalmsens.data.Measurement][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('measurement_end', callback=callback)

    def on_curve_begin(self, callback: Callable[[Curve], None]) -> EventHandle:
        """Register a callback to invoke at the start of a new curve.

        For EIS use `on_eis_data_start`.

        Parameters
        ----------
        callback : Callable[[Curve]]
            The function to call when triggered.
            Passes [pypalmsens.data.Curve][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('curve_begin', callback=callback)

    def on_curve_new_data(self, callback: Callable[[CallbackData], None]) -> EventHandle:
        """Register a callback to invoke when new data are received

        Note that the data are batched depending on available resources.

        For EIS use `on_eis_new_data`.

        Parameters
        ----------
        callback : Callable[[CallbackData]]
            The function to call when triggered.
            Passes [pypalmsens.data.CallbackData][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('curve_new_data', callback=callback)

    def on_curve_end(self, callback: Callable[[Curve], None]) -> EventHandle:
        """Register a callback to invoke at the end of a curve.

        For EIS use `on_eis_data_end`.

        Parameters
        ----------
        callback : Callable[[Curve]]
            The function to call when triggered.
            Passes [pypalmsens.data.Curve][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('curve_end', callback=callback)

    def on_eis_data_begin(self, callback: Callable[[EISData], None]) -> EventHandle:
        """Register a callback to invoke at the start of a new EIS data set.

        Parameters
        ----------
        callback : Callable[[EISData]]
            The function to call when triggered.
            Passes [pypalmsens.data.EISData][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('eis_data_begin', callback=callback)

    def on_eis_new_data(self, callback: Callable[[CallbackDataEIS], None]) -> EventHandle:
        """Register a callback to invoke when new eis data are received.

        Data points are batched depending on available resources.

        Parameters
        ----------
        callback : Callable[[CallbackDataEIS]]
            The function to call when triggered.
            Passes [pypalmsens.data.CallbackDataEIS][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('eis_new_data', callback=callback)

    def on_eis_data_end(self, callback: Callable[[], None]) -> EventHandle:
        """Register a callback to invoke at the end of an EIS data set.

        Parameters
        ----------
        callback : Callable
            The function to call when triggered.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('eis_data_end', callback=callback)

    def on_measurement_setup(self, callback: Callable[[], None]) -> EventHandle:
        """Register a callback to invoke before the measurement starts.

        Use this to set up file resources, database connections, etc.

        Parameters
        ----------
        callback : Callable
            The function to call when triggered.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('measurement_setup', callback=callback)

    def on_measurement_teardown(self, callback: Callable[[], None]) -> EventHandle:
        """Register a callback to invoke after the measurement ends.

        The measurement ends when it finnished successfully or after an error occurs.
        Use this to close files or clean up resources.

        Parameters
        ----------
        callback : Callable
            The function to call when triggered.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('measurement_teardown', callback=callback)

    def on_receive_message(self, callback: Callable[[str], None], /):
        """Register a callback for when a new message is received.

        The callback will be invoked, for example, when a method is started,
        or when `send_string` is called in MethodSCRIPT.

        Parameters
        ----------
        callback : callable[[str]]
            The function to call when triggered.
            Passes [str][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('receive_message', callback=callback)

    def on_receive_status(self, callback: Callable[[Status], None], /):
        """Register a callback for idle status update events.

        Requires active event loop (i.e. async only).

        The callback will be invoked whenever the instrument sends
        updated current/potential values during idle state or pretreatment phases.
        The update frequency varies per device.

        Parameters
        ----------
        callback : callable[[Status]]
            The function to call when triggered.
            Passes [pypalmsens.data.Status][] as argument to the callback.

        Returns
        -------
        EventHandle
            Handle that can be used to cancel the subscription.
        """
        return self.on('receive_status', callback=callback)
