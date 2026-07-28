from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from typing_extensions import override

from ..data import Curve, EISData, Measurement
from .callback import CallbackData, CallbackDataEIS

AllowedEvents = Literal[
    'error',
    'measurement_begin',
    'measurement_end',
    'curve_begin',
    'curve_new_data',
    'curve_end',
    'eis_data_begin',
    'eis_new_data',
    'eis_data_end',
    'measurement_setup',
    'measurement_teardown',
    'receive_message',
    'receive_status',
]


@dataclass
class EventHandle:
    emitter: EventsMixin
    event: AllowedEvents
    callback: Callable[..., None]

    def cancel(self) -> None:
        self.emitter._listeners[self.event].remove(self.callback)


@dataclass
class EventHandleReceiveMessage(EventHandle):
    def __post_init__(self):
        self.emitter._comm.ClientConnection.ReceiveMessage += self._receive_message_handler

    def _receive_message_handler(self, sender, message: str) -> None:
        """Message handler helper function to schedule the callback."""
        self.callback(message)

    @override
    def cancel(self):
        self.emitter._comm.ClientConnection.ReceiveMessage -= self._receive_message_handler


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
