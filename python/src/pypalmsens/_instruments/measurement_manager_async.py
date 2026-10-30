from __future__ import annotations

import asyncio
import weakref
from collections import defaultdict
from collections.abc import Callable, Generator
from contextlib import contextmanager
from io import BufferedWriter
from pathlib import Path
from typing import Any, Final

import PalmSens
import System
from PalmSens import AsyncEventHandler, Plottables
from PalmSens.Comm import CommManager
from pydantic import ConfigDict, TypeAdapter
from pydantic.dataclasses import dataclass
from System import EventHandler
from System.Threading.Tasks import Task

from .._data import DataSet
from .._methods.energy import BaseMethodScriptTechnique
from .._types import AllowedEvents, MethodTypeCompatible
from ..data import Curve, DataArray, EISData, Measurement
from .callback import Callback, CallbackData, CallbackDataEIS, CallbackEIS, DataRow
from .shared import wrap_task


@dataclass(
    kw_only=True,
    config=ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    ),
)
class JSONWriter:
    """Set up measurement events for streaming to JSON Lines format

    More information: https://jsonlines.org/
    """

    filename: Path | str
    """Path to stream to."""

    _stream: BufferedWriter | None = None
    _adapter: TypeAdapter[DataRow] = TypeAdapter(DataRow)

    def append_to_callbacks(self, callbacks: dict[AllowedEvents, list[Callable[..., None]]]):
        callbacks['measurement_begin'].append(self.on_measurement_begin)
        callbacks['curve_begin'].append(self.on_curve_begin)
        callbacks['curve_new_data'].append(self.on_curve_new_data)
        callbacks['eis_data_begin'].append(self.on_eis_data_begin)
        callbacks['eis_new_data'].append(self.on_eis_new_data)
        callbacks['measurement_setup'].append(self.setup)
        callbacks['measurement_teardown'].append(self.teardown)

    def on_measurement_begin(self, measurement: Measurement):
        assert self._stream
        _ = self._stream.write(measurement.metadata_json())
        _ = self._stream.write(b'\n')

        self._stream.flush()

    def on_curve_begin(self, curve: Curve):
        assert self._stream
        _ = self._stream.write(curve.metadata_json())
        _ = self._stream.write(b'\n')

        self._stream.flush()

    def on_curve_new_data(self, data: CallbackData):
        assert self._stream
        for row in data._streaming_rows():
            _ = self._stream.write(self._adapter.dump_json(row))
            _ = self._stream.write(b'\n')

        self._stream.flush()

    def on_eis_data_begin(self, eis_data: EISData):
        assert self._stream
        _ = self._stream.write(eis_data.metadata_json())
        _ = self._stream.write(b'\n')
        self._stream.flush()

    def on_eis_new_data(self, data: CallbackDataEIS):
        assert self._stream
        for row in data._streaming_rows():
            _ = self._stream.write(self._adapter.dump_json(row))
            _ = self._stream.write(b'\n')
        self._stream.flush()

    def setup(self):
        self._stream = open(self.filename, 'wb')  # noqa: SIM115

    def teardown(self):
        assert self._stream
        self._stream.close()


class MeasurementManagerAsync:
    """Measurement helper class that manages the instrument communication and handles events."""

    def __init__(
        self,
        *,
        comm: CommManager,
    ):
        self.comm: CommManager = comm
        self.callback: Callback | CallbackEIS | None = None

        self.is_measuring: bool = False
        self.active_measurement: Measurement | None = None

        self.loop: asyncio.AbstractEventLoop

        self.begin_measurement_event: asyncio.Event
        self.end_measurement_event: asyncio.Event

        self.event_handlers: Final = self.setup_handlers()
        self.callbacks: dict[AllowedEvents, list[Callable[..., None]]] = defaultdict(list)

        self.eis_last_data_index: int = 0

    def setup_handlers(self) -> dict:
        """Create delegates that do not keep a strong reference to this instance.

        The delegates are stored in `self.event_handlers`, and the .NET
        CommManager / Plottables objects hold on to some of them. A bound method
        would therefore create a reference cycle that crosses the Python/CLR
        boundary, which neither garbage collector can traverse.
        """

        def bind(name: str, fallback: Any = None) -> Callable[..., Any]:
            ref = weakref.WeakMethod(getattr(self, name))

            def dispatch(*args: Any) -> Any:
                fn = ref()
                # manager already collected: ignore late events
                if fn is None:
                    return fallback
                return fn(*args)

            dispatch.__name__ = f'weak_{name}'
            dispatch.__qualname__ = f'MeasurementManagerAsync.{name}'
            return dispatch

        def bind_async(name: str) -> Callable[..., Any]:
            # the CLR awaits these, so they must always return a Task
            return bind(name, fallback=Task.CompletedTask)

        return {
            'measurement_begin': AsyncEventHandler[CommManager.BeginMeasurementEventArgsAsync](
                bind_async('on_measurement_begin_event')
            ),
            'measurement_end': AsyncEventHandler[CommManager.EndMeasurementAsyncEventArgs](
                bind_async('on_measurement_end_event')
            ),
            'curve_begin': Plottables.CurveEventHandler(bind('on_curve_begin_event')),
            'curve_new_data': Plottables.Curve.NewDataAddedEventHandler(
                bind('on_curve_new_data_event')
            ),
            'curve_end': EventHandler(bind('on_curve_end_event')),
            'eis_data_begin': Plottables.EISDataEventHandler(bind('on_eis_data_begin_event')),
            'eis_new_data': Plottables.EISData.NewDataEventHandler(
                bind('on_eis_new_data_event')
            ),
            'eis_data_end': EventHandler(bind('on_eis_data_end_event')),
            'error': EventHandler(bind('on_error_event')),
        }

    def setup(self):
        """Subscribe to events indicating the start and end of the measurement."""
        self.is_measuring = True
        self.comm.BeginMeasurementAsync += self.event_handlers['measurement_begin']
        self.comm.EndMeasurementAsync += self.event_handlers['measurement_end']
        self.comm.Disconnected += self.event_handlers['error']

        if (
            self.callbacks['eis_data_begin']
            or self.callbacks['eis_new_data']
            or self.callbacks['eis_data_end']
        ):
            self.comm.BeginReceiveEISData += self.event_handlers['eis_data_begin']

        if (
            self.callbacks['curve_begin']
            or self.callbacks['curve_new_data']
            or self.callbacks['curve_end']
        ):
            self.comm.BeginReceiveCurve += self.event_handlers['curve_begin']

    def teardown(self):
        """Unsubscribe to events indicating the start and end of the measurement."""
        self.comm.BeginMeasurementAsync -= self.event_handlers['measurement_begin']
        self.comm.EndMeasurementAsync -= self.event_handlers['measurement_end']
        self.comm.Disconnected -= self.event_handlers['error']

        if (
            self.callbacks['eis_data_begin']
            or self.callbacks['eis_new_data']
            or self.callbacks['eis_data_end']
        ):
            self.comm.BeginReceiveEISData -= self.event_handlers['eis_data_begin']

        if (
            self.callbacks['curve_begin']
            or self.callbacks['curve_new_data']
            or self.callbacks['curve_end']
        ):
            self.comm.BeginReceiveCurve -= self.event_handlers['curve_begin']

        self.is_measuring = False

    @contextmanager
    def _measurement_context(self) -> Generator[None, Any, Any]:
        """Context manager to manage the connection to the communication object."""
        try:
            for setup in self.callbacks['measurement_setup']:
                setup()

            self.setup()

            yield

        except Exception:
            if self.comm.ClientConnection.Semaphore.CurrentCount == 0:
                _ = self.comm.ClientConnection.Semaphore.Release()

            raise

        finally:
            self.teardown()

            for teardown in self.callbacks['measurement_teardown']:
                teardown()

    async def await_measurement(
        self,
        method: PalmSens.Method,
        sync_event: asyncio.Event | None = None,
    ):
        """Helper function to handle the measurement.

        Obtaining a lock on the `ClientConnection` (via semaphore) is required when
        communicating with the instrument."""
        await wrap_task(self.comm.ClientConnection.Semaphore.WaitAsync())

        _ = await wrap_task(self.comm.MeasureAsync(method))

        _ = self.comm.ClientConnection.Semaphore.Release()

        _ = await self.begin_measurement_event.wait()

        if sync_event is not None:
            sync_event.set()

        _ = await self.end_measurement_event.wait()

    async def measure(
        self,
        method: MethodTypeCompatible,
        callback: Callback | CallbackEIS | None = None,
        sync_event: asyncio.Event | None = None,
        stream: Path | str | None = None,
        listeners: dict[AllowedEvents, list[Callable[..., None]]] | None = None,
    ) -> Measurement:
        """Measure given method.

        Parameters
        ----------
        method: MethodType
            Method parameters for measurement
        callback: Callback, optional
            Gets called every time new data is added
        sync_event: Event, optional
            Used to pass event for hardware synchronization

        Returns
        -------
        measurement : Measurement
        """
        psmethod = method._to_psmethod()

        self.loop = asyncio.get_running_loop()
        self.begin_measurement_event = asyncio.Event()
        self.end_measurement_event = asyncio.Event()

        if stream:
            JSONWriter(filename=stream).append_to_callbacks(self.callbacks)

        if listeners:
            for name, cbs in listeners.items():
                self.callbacks[name].extend(cbs)

        if callback:
            if method.id in ('eis', 'gis', 'fis', 'fgis'):
                self.callbacks['eis_new_data'].append(callback)
            else:
                self.callbacks['curve_new_data'].append(callback)

        with self._measurement_context():
            await self.await_measurement(method=psmethod, sync_event=sync_event)

        assert self.active_measurement

        if isinstance(method, BaseMethodScriptTechnique):
            self.active_measurement._inner.Title = method._name  # type: ignore

        try:
            return self.active_measurement
        finally:
            # clear circular reference
            self.active_measurement = None
            self.event_handlers.clear()

    def on_measurement_begin_event(
        self, sender: PalmSens.Comm.CommManager, args
    ) -> Task.CompletedTask:
        """Called when the measurement begins."""
        measurement = Measurement._wrap(args.NewMeasurement)

        self.active_measurement = measurement

        _ = self.loop.call_soon_threadsafe(self.begin_measurement_event.set)

        for callback in self.callbacks['measurement_begin']:
            callback(measurement)

        return Task.CompletedTask

    def on_measurement_end_event(
        self, comm: PalmSens.Comm.CommManager, args
    ) -> Task.CompletedTask:
        """Called when the measurement ends."""

        for callback in self.callbacks['measurement_end']:
            _ = self.loop.call_soon_threadsafe(callback, self.active_measurement)

        _ = self.loop.call_soon_threadsafe(self.end_measurement_event.set)

        return Task.CompletedTask

    def on_curve_new_data_event(
        self,
        pscurve: Plottables.Curve,
        args: PalmSens.Data.ArrayDataAddedEventArgs,
    ):
        """Called when new data is added to the curve."""

        data = CallbackData(
            x_array=DataArray._wrap(pscurve.XAxisDataArray),
            y_array=DataArray._wrap(pscurve.YAxisDataArray),
            start=args.StartIndex,
            id=pscurve.GetHashCode(),
        )

        for callback in self.callbacks['curve_new_data']:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def on_curve_end_event(
        self,
        pscurve: Plottables.Curve,
        args: PalmSens.FinishedEventArgs,
    ):
        """Unsubscribe to curve finished / new data added events."""
        pscurve.NewDataAdded -= self.event_handlers['curve_new_data']
        pscurve.Finished -= self.event_handlers['curve_end']

        curve = Curve._wrap(pscurve)

        for callback in self.callbacks['curve_end']:
            _ = self.loop.call_soon_threadsafe(callback, curve)  # type: ignore

    def on_curve_begin_event(
        self,
        sender: PalmSens.Comm.CommManager,
        args: PalmSens.Plottables.CurveEventArgs,
    ):
        """Subscribe to curve finished / new data added events."""
        pscurve = args.GetCurve()
        pscurve.NewDataAdded += self.event_handlers['curve_new_data']
        pscurve.Finished += self.event_handlers['curve_end']

        curve = Curve._wrap(pscurve)

        for callback in self.callbacks['curve_begin']:
            _ = self.loop.call_soon_threadsafe(callback, curve)  # type: ignore

    def on_eis_new_data_event(self, eis_data: Plottables.EISData, args):
        """Called when a new EIS data points is obtained. Requires a callback."""
        # This event is sometimes fired twice, once for raw data
        # and once again for derived data. This leads to duplicate data points
        # in the callback and/or arrays with different lengths.
        # - `eis_data.EISDataSet.NPoints` arbitrarily matches either derived
        #     or non-derived array length -> cannot be used as a reliable pointer
        # - `args.Index` works and is unique, but always lags behind.
        #    It either points to derived or non-derived array,
        #    so there is a chance to miss last data point
        # Instead use count of non-derived array (e.g. Time)
        # for a reliable pointer to track the last array index
        count = eis_data.EISDataSet.GetLastTimeDataArray().Count

        # Skip event if pointer has not moved
        if count == self.eis_last_data_index:
            return

        data = CallbackDataEIS(
            data=DataSet._wrap(eis_data.EISDataSet),
            start=self.eis_last_data_index,
            index=count - 1,
            id=eis_data.GetHashCode(),
        )

        self.eis_last_data_index = count

        for callback in self.callbacks['eis_new_data']:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def on_eis_data_end_event(
        self,
        eis_data: Plottables.EISData,
        args: PalmSens.FinishedEventArgs,
    ):
        """Unsubscribes to EIS data events."""
        eis_data.NewDataAdded -= self.event_handlers['eis_new_data']
        eis_data.Finished -= self.event_handlers['eis_data_end']

        for callback in self.callbacks['eis_data_end']:
            _ = self.loop.call_soon_threadsafe(callback)  # type: ignore

    def on_eis_data_begin_event(
        self,
        sender: PalmSens.Comm.CommManager,
        eis_data: Plottables.EISData,
    ):
        """Subscribes to EIS data events."""
        eis_data.NewDataAdded += self.event_handlers['eis_new_data']
        eis_data.Finished += self.event_handlers['eis_data_end']

        self.eis_last_data_index = 0

        data = EISData._wrap(eis_data)

        for callback in self.callbacks['eis_data_begin']:
            _ = self.loop.call_soon_threadsafe(callback, data)

    def on_error_event(self, sender: PalmSens.Comm.CommManager, args: System.EventArgs):
        """Called when a communication error occurs."""

        for callback in self.callbacks['error']:
            _ = self.loop.call_soon_threadsafe(callback)

        def teardown_and_raise():
            self.begin_measurement_event.set()
            self.end_measurement_event.set()

            raise ConnectionError('Measurement failed due to a communication or parsing error')

        _ = self.loop.call_soon_threadsafe(teardown_and_raise)
