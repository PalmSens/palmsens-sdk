from __future__ import annotations

import asyncio
from contextlib import contextmanager
from io import BufferedWriter
from pathlib import Path
from typing import Any, Callable, Generator

import PalmSens
import System
from PalmSens import AsyncEventHandler, Plottables
from PalmSens.Comm import CommManager
from pydantic import ConfigDict, Field, TypeAdapter
from pydantic.dataclasses import dataclass
from System import EventHandler
from System.Threading.Tasks import Task

from pypalmsens._methods.energy import BaseMethodScriptTechnique
from pypalmsens._types import MethodTypeCompatible

from .._data import DataSet
from ..data import Curve, DataArray, EISData, Measurement
from .callback import Callback, CallbackData, CallbackDataEIS, CallbackEIS, DataRow
from .shared import create_future


@dataclass(
    kw_only=True,
    config=ConfigDict(
        validate_assignment=True,
    ),
)
class MeasurementEvents:
    """Register callbacks to measurement events.

    For non-impedimetric measurements, use:
        - `on_curve_begin`
        - `on_curve_new_data`
        - `on_curve_end`

    For impedimetric measurements, use:
        - `on_eis_data_begin`
        - `on_eis_new_data`
        - `on_eis_data_end`
    """

    on_error: Callable[[], None] | None = None
    """Called when a connection or communication error occurs."""

    on_measurement_begin: Callable[[Measurement], None] | None = None
    """Called at the start of a measurement."""

    on_measurement_end: Callable[[], None] | None = None
    """Called at the end of a measurement."""

    on_curve_begin: Callable[[Curve], None] | None = None
    """Called at the start of a new curve (for EIS use on_eis_data_start)."""

    on_curve_new_data: Callable[[CallbackData], None] | None = None
    """Called when new data are received (for EIS use on_eis_new_data).

    Note that the data are batched depending on available resources."""

    on_curve_end: Callable[[Curve], None] | None = None
    """Called at the end of a curve (for EIS use on_eis_data_end)."""

    on_eis_data_begin: Callable[[EISData], None] | None = None
    """Called at the start of a new EIS data set."""

    on_eis_new_data: Callable[[CallbackDataEIS], None] | None = None
    """Called when new eis data are received.

    Data points are batched depending on available resources."""

    on_eis_data_end: Callable[[], None] | None = None
    """Called at the end of an EIS data set."""

    setup: Callable[[], None] | None = None
    """
    Called before the measurement starts.

    Use this to set up file resources, database connections, etc."""

    teardown: Callable[[], None] | None = None
    """Called after the measurement has ended, either succesfully or after an error occurs.

    Use this to close files or clean up resources."""

    def add_to(self, other: CallbackManager):
        if self.on_error:
            other.on_error.append(self.on_error)
        if self.on_measurement_begin:
            other.on_measurement_begin.append(self.on_measurement_begin)
        if self.on_measurement_end:
            other.on_measurement_end.append(self.on_measurement_end)
        if self.on_curve_begin:
            other.on_curve_begin.append(self.on_curve_begin)
        if self.on_curve_new_data:
            other.on_curve_new_data.append(self.on_curve_new_data)
        if self.on_curve_end:
            other.on_curve_end.append(self.on_curve_end)
        if self.on_eis_data_begin:
            other.on_eis_data_begin.append(self.on_eis_data_begin)
        if self.on_eis_new_data:
            other.on_eis_new_data.append(self.on_eis_new_data)
        if self.on_eis_data_end:
            other.on_eis_data_end.append(self.on_eis_data_end)
        if self.setup:
            other.setup.append(self.setup)
        if self.teardown:
            other.teardown.append(self.teardown)


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

    def add_to(self, other: CallbackManager):
        other.on_measurement_begin.append(self.on_measurement_begin)
        other.on_curve_begin.append(self.on_curve_begin)
        other.on_curve_new_data.append(self.on_curve_new_data)
        other.on_eis_data_begin.append(self.on_eis_data_begin)
        other.on_eis_new_data.append(self.on_eis_new_data)
        other.setup.append(self.setup)
        other.teardown.append(self.teardown)

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
        self._stream = open(self.filename, 'wb')

    def teardown(self):
        assert self._stream
        self._stream.close()


@dataclass(
    kw_only=True,
    config=ConfigDict(
        validate_assignment=True,
    ),
)
class CallbackManager:
    """Dataclass to manage callbacks."""

    on_error: list[Callable[[], None]] = Field(default_factory=list)
    on_measurement_begin: list[Callable[[Measurement], None]] = Field(default_factory=list)
    on_measurement_end: list[Callable[[], None]] = Field(default_factory=list)
    on_curve_begin: list[Callable[[Curve], None]] = Field(default_factory=list)
    on_curve_new_data: list[Callable[[CallbackData], None]] = Field(default_factory=list)
    on_curve_end: list[Callable[[Curve], None]] = Field(default_factory=list)
    on_eis_data_begin: list[Callable[[EISData], None]] = Field(default_factory=list)
    on_eis_new_data: list[Callable[[CallbackDataEIS], None]] = Field(default_factory=list)
    on_eis_data_end: list[Callable[[], None]] = Field(default_factory=list)
    setup: list[Callable[[], None]] = Field(default_factory=list)
    teardown: list[Callable[[], None]] = Field(default_factory=list)


class MeasurementManagerAsync:
    """Measurement helper class that manages the instrument communication and handles events."""

    callbacks: CallbackManager

    def __init__(
        self,
        *,
        comm: CommManager,
    ):
        self.comm: CommManager = comm
        self.callback: Callback | CallbackEIS | None = None

        self.is_measuring: bool = False
        self.last_measurement: Measurement | None = None

        self.loop: asyncio.AbstractEventLoop

        self.begin_measurement_event: asyncio.Event
        self.end_measurement_event: asyncio.Event

        self.setup_handlers()

        self.eis_last_data_index: int = 0

    def setup_handlers(self):
        self.begin_measurement_handler: AsyncEventHandler = AsyncEventHandler[
            CommManager.BeginMeasurementEventArgsAsync
        ](self.begin_measurement_callback)

        self.end_measurement_handler: AsyncEventHandler = AsyncEventHandler[
            CommManager.EndMeasurementAsyncEventArgs
        ](self.end_measurement_callback)

        self.begin_receive_curve_handler: EventHandler = Plottables.CurveEventHandler(
            self.begin_receive_curve_callback
        )
        self.curve_data_added_handler: EventHandler = Plottables.Curve.NewDataAddedEventHandler(
            self.curve_data_added_callback
        )
        self.curve_finished_handler: EventHandler = EventHandler(self.curve_finished_callback)

        self.begin_receive_eis_data_handler: EventHandler = Plottables.EISDataEventHandler(
            self.begin_receive_eis_data_callback
        )
        self.eis_data_data_added_handler: EventHandler = Plottables.EISData.NewDataEventHandler(
            self.eis_data_data_added_callback
        )
        self.eis_data_finished_handler: EventHandler = EventHandler(
            self.eis_data_finished_callback
        )

        self.comm_error_handler: EventHandler = EventHandler(self.comm_error_callback)

    def setup(self):
        """Subscribe to events indicating the start and end of the measurement."""
        self.is_measuring = True
        self.comm.BeginMeasurementAsync += self.begin_measurement_handler
        self.comm.EndMeasurementAsync += self.end_measurement_handler
        self.comm.Disconnected += self.comm_error_handler

        if self.callbacks.on_eis_new_data:
            self.comm.BeginReceiveEISData += self.begin_receive_eis_data_handler

        if self.callbacks.on_curve_new_data:
            self.comm.BeginReceiveCurve += self.begin_receive_curve_handler

    def teardown(self):
        """Unsubscribe to events indicating the start and end of the measurement."""
        self.comm.BeginMeasurementAsync -= self.begin_measurement_handler
        self.comm.EndMeasurementAsync -= self.end_measurement_handler
        self.comm.Disconnected -= self.comm_error_handler

        if self.callbacks.on_eis_new_data:
            self.comm.BeginReceiveEISData -= self.begin_receive_eis_data_handler

        if self.callbacks.on_curve_new_data:
            self.comm.BeginReceiveCurve -= self.begin_receive_curve_handler

        self.is_measuring = False

    @contextmanager
    def _measurement_context(self) -> Generator[None, Any, Any]:
        """Context manager to manage the connection to the communication object."""
        try:
            for setup in self.callbacks.setup:
                setup()

            self.setup()

            yield

        except Exception:
            if self.comm.ClientConnection.Semaphore.CurrentCount == 0:
                _ = self.comm.ClientConnection.Semaphore.Release()

            raise

        finally:
            self.teardown()

            for teardown in self.callbacks.teardown:
                teardown()

    async def await_measurement(
        self,
        method: PalmSens.Method,
        sync_event: asyncio.Event | None = None,
    ):
        """Helper function to handle the measurement.

        Obtaining a lock on the `ClientConnection` (via semaphore) is required when
        communicating with the instrument."""
        await create_future(self.comm.ClientConnection.Semaphore.WaitAsync())

        _ = await create_future(self.comm.MeasureAsync(method))

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
        events: MeasurementEvents | None = None,
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

        self.callbacks = CallbackManager()

        if stream:
            JSONWriter(filename=stream).add_to(self.callbacks)

        if events:
            events.add_to(self.callbacks)

        if callback:
            if method.id in ('eis', 'geis', 'fis', 'fgis'):
                self.callbacks.on_eis_new_data.append(callback)  # type: ignore
            else:
                self.callbacks.on_curve_new_data.append(callback)  # type: ignore

        with self._measurement_context():
            await self.await_measurement(method=psmethod, sync_event=sync_event)

        assert self.last_measurement

        if isinstance(method, BaseMethodScriptTechnique):
            self.last_measurement._psmeasurement.Title = method._name  # type: ignore

        return self.last_measurement

    def begin_measurement_callback(
        self, sender: PalmSens.Comm.CommManager, args
    ) -> Task.CompletedTask:
        """Called when the measurement begins."""
        measurement = Measurement(psmeasurement=args.NewMeasurement)

        self.last_measurement = measurement

        _ = self.loop.call_soon_threadsafe(self.begin_measurement_event.set)

        for callback in self.callbacks.on_measurement_begin:
            callback(measurement)

        return Task.CompletedTask

    def end_measurement_callback(
        self, comm: PalmSens.Comm.CommManager, args
    ) -> Task.CompletedTask:
        """Called when the measurement ends."""

        _ = self.loop.call_soon_threadsafe(self.end_measurement_event.set)

        for callback in self.callbacks.on_measurement_end:
            _ = self.loop.call_soon_threadsafe(callback)

        return Task.CompletedTask

    def curve_data_added_callback(
        self,
        pscurve: Plottables.Curve,
        args: PalmSens.Data.ArrayDataAddedEventArgs,
    ):
        """Called when new data is added to the curve."""

        data = CallbackData(
            x_array=DataArray(psarray=pscurve.XAxisDataArray),
            y_array=DataArray(psarray=pscurve.YAxisDataArray),
            start=args.StartIndex,
            id=pscurve.GetHashCode(),
        )

        for callback in self.callbacks.on_curve_new_data:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def curve_finished_callback(
        self,
        pscurve: Plottables.Curve,
        args: PalmSens.FinishedEventArgs,
    ):
        """Unsubscribe to curve finished / new data added events."""
        pscurve.NewDataAdded -= self.curve_data_added_handler
        pscurve.Finished -= self.curve_finished_handler

        curve = Curve(pscurve=pscurve)

        for callback in self.callbacks.on_curve_end:
            _ = self.loop.call_soon_threadsafe(callback, curve)  # type: ignore

    def begin_receive_curve_callback(
        self,
        sender: PalmSens.Comm.CommManager,
        args: PalmSens.Plottables.CurveEventArgs,
    ):
        """Subscribe to curve finished / new data added events."""
        pscurve = args.GetCurve()
        pscurve.NewDataAdded += self.curve_data_added_handler
        pscurve.Finished += self.curve_finished_handler

        curve = Curve(pscurve=pscurve)

        for callback in self.callbacks.on_curve_begin:
            _ = self.loop.call_soon_threadsafe(callback, curve)  # type: ignore

    def eis_data_data_added_callback(self, eis_data: Plottables.EISData, args):
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
            data=DataSet(psdataset=eis_data.EISDataSet),
            start=self.eis_last_data_index,
            index=count - 1,
            id=eis_data.GetHashCode(),
        )

        self.eis_last_data_index = count

        for callback in self.callbacks.on_eis_new_data:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def eis_data_finished_callback(
        self,
        eis_data: Plottables.EISData,
        args: PalmSens.FinishedEventArgs,
    ):
        """Unsubscribes to EIS data events."""
        eis_data.NewDataAdded -= self.eis_data_data_added_handler
        eis_data.Finished -= self.eis_data_finished_handler

        for callback in self.callbacks.on_eis_data_end:
            _ = self.loop.call_soon_threadsafe(callback)  # type: ignore

    def begin_receive_eis_data_callback(
        self,
        sender: PalmSens.Comm.CommManager,
        eis_data: Plottables.EISData,
    ):
        """Subscribes to EIS data events."""
        eis_data.NewDataAdded += self.eis_data_data_added_handler
        eis_data.Finished += self.eis_data_finished_handler

        self.eis_last_data_index = 0

        data = EISData(pseis=eis_data)

        for callback in self.callbacks.on_eis_data_begin:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def comm_error_callback(self, sender: PalmSens.Comm.CommManager, args: System.EventArgs):
        """Called when a communication error occurs."""

        for callback in self.callbacks.on_error:
            _ = self.loop.call_soon_threadsafe(callback)

        def teardown_and_raise():
            self.begin_measurement_event.set()
            self.end_measurement_event.set()

            raise ConnectionError('Measurement failed due to a communication or parsing error')

        _ = self.loop.call_soon_threadsafe(teardown_and_raise)
