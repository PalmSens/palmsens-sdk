from __future__ import annotations

import asyncio
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Generator

import PalmSens
import System
from PalmSens import AsyncEventHandler, Plottables
from PalmSens.Comm import CommManager
from pydantic import ConfigDict, Field, TypeAdapter, computed_field
from pydantic.dataclasses import dataclass
from System import EventHandler
from System.Threading.Tasks import Task

from pypalmsens._methods.energy import BaseMethodScriptTechnique
from pypalmsens._types import MethodTypeCompatible

from .._data import DataSet
from ..data import Curve, DataArray, EISData, Measurement
from .callback import Callback, CallbackData, CallbackDataEIS, CallbackEIS, DataRow
from .shared import create_future


@dataclass
class Callbacks:
    """Dataclass to manage callbacks."""

    comm_error: list[Callable[[], None]] = Field(default_factory=list)
    """Called when a connection error occurs."""
    measurement_begin: list[Callable[[Measurement], None]] = Field(default_factory=list)
    """Called at the start of a measurement."""
    measurement_end: list[Callable[[], None]] = Field(default_factory=list)
    """Called at the end of a measurement."""
    curve_start: list[Callable[[Curve], None]] = Field(default_factory=list)
    """Called at the start of a new curve."""
    curve_new_data: list[Callable[[CallbackData], None]] = Field(default_factory=list)
    """Called when new data are received.

    Note that the data are batched depending on available resources."""
    curve_finished: list[Callable[[Curve], None]] = Field(default_factory=list)
    """Called ant the end of a curve."""
    eis_data_start: list[Callable[[EISData], None]] = Field(default_factory=list)
    """Called at the start of an EIS data set."""
    eis_data_new_data: list[Callable[[CallbackDataEIS], None]] = Field(default_factory=list)
    """Called when new data are received.

    Note that the data are batched depending on available resources."""
    eis_data_end: list[Callable[[], None]] = Field(default_factory=list)
    """Called at the end of an EIS data set."""
    setup: list[Callable[[], None]] = Field(default_factory=list)
    """
    Called before the measurement starts.

    Use this to set up file resources, database connections, etc."""
    teardown: list[Callable[[], None]] = Field(default_factory=list)
    """Called after the measurement has ended, either succesfully or after an error occurs.

    Use this to close files or clean up resources."""

    def append(self, other: Callbacks):
        self.comm_error.extend(other.comm_error)
        self.measurement_begin.extend(other.measurement_begin)
        self.measurement_end.extend(other.measurement_end)
        self.curve_start.extend(other.curve_start)
        self.curve_new_data.extend(other.curve_new_data)
        self.curve_finished.extend(other.curve_finished)
        self.eis_data_start.extend(other.eis_data_start)
        self.eis_data_new_data.extend(other.eis_data_new_data)
        self.eis_data_end.extend(other.eis_data_end)
        self.setup.extend(other.setup)
        self.teardown.extend(other.teardown)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class JSONWriter:
    filename: Path | str
    """File to write to."""
    _stream: BytesIO | None = None
    _adapter: TypeAdapter[DataRow] = TypeAdapter(DataRow)

    @computed_field
    @property
    def callbacks(self) -> Callbacks:
        return Callbacks(
            measurement_begin=[self._write_measurement_metadata_to_stream],
            curve_start=[self._write_curve_metadata_to_stream],
            curve_new_data=[self._write_data_to_stream],
            eis_data_start=[self._write_eis_metadata_to_stream],
            eis_data_new_data=[self._write_eis_data_to_stream],
            setup=[self._stream_open],
            teardown=[self._stream_close],
        )

    def _write_curve_metadata_to_stream(self, curve: Curve):
        assert self._stream
        _ = self._stream.write(curve.metadata_json())
        _ = self._stream.write(b'\n')

        self._stream.flush()

    def _write_measurement_metadata_to_stream(self, measurement: Measurement):
        assert self._stream
        _ = self._stream.write(measurement.metadata_json())
        _ = self._stream.write(b'\n')

        self._stream.flush()

    def _write_data_to_stream(self, data: CallbackData):
        assert self._stream
        for row in data._streaming_rows():
            _ = self._stream.write(self._adapter.dump_json(row))
            _ = self._stream.write(b'\n')

        self._stream.flush()

    def _write_eis_metadata_to_stream(self, eis_data: EISData):
        assert self._stream
        _ = self._stream.write(eis_data.metadata_json())
        _ = self._stream.write(b'\n')
        self._stream.flush()

    def _write_eis_data_to_stream(self, data: CallbackDataEIS):
        assert self._stream
        for row in data._streaming_rows():
            _ = self._stream.write(self._adapter.dump_json(row))
            _ = self._stream.write(b'\n')
        self._stream.flush()

    def _stream_open(self):
        self._stream = open(self.filename, 'wb')

    def _stream_close(self):
        assert self._stream
        self._stream.close()


class MeasurementManagerAsync:
    """Measurement helper class that manages the instrument communication and handles events."""

    callbacks: Callbacks

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

        if self.callbacks.eis_data_new_data:
            self.comm.BeginReceiveEISData += self.begin_receive_eis_data_handler

        if self.callbacks.curve_new_data:
            self.comm.BeginReceiveCurve += self.begin_receive_curve_handler

    def teardown(self):
        """Unsubscribe to events indicating the start and end of the measurement."""
        self.comm.BeginMeasurementAsync -= self.begin_measurement_handler
        self.comm.EndMeasurementAsync -= self.end_measurement_handler
        self.comm.Disconnected -= self.comm_error_handler

        if self.callbacks.eis_data_new_data:
            self.comm.BeginReceiveEISData -= self.begin_receive_eis_data_handler

        if self.callbacks.curve_new_data:
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

        self.callbacks = Callbacks()

        if stream:
            self.callbacks.append(JSONWriter(filename=stream).callbacks)

        if callback:
            if method.id in ('eis', 'geis', 'fis', 'fgis'):
                self.callbacks.eis_data_new_data.append(callback)  # type: ignore
            else:
                self.callbacks.curve_new_data.append(callback)  # type: ignore

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

        for callback in self.callbacks.measurement_begin:
            callback(measurement)

        return Task.CompletedTask

    def end_measurement_callback(
        self, comm: PalmSens.Comm.CommManager, args
    ) -> Task.CompletedTask:
        """Called when the measurement ends."""

        _ = self.loop.call_soon_threadsafe(self.end_measurement_event.set)

        for callback in self.callbacks.measurement_end:
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

        for callback in self.callbacks.curve_new_data:
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

        for callback in self.callbacks.curve_finished:
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

        for callback in self.callbacks.curve_start:
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

        for callback in self.callbacks.eis_data_new_data:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def eis_data_finished_callback(
        self,
        eis_data: Plottables.EISData,
        args: PalmSens.FinishedEventArgs,
    ):
        """Unsubscribes to EIS data events."""
        eis_data.NewDataAdded -= self.eis_data_data_added_handler
        eis_data.Finished -= self.eis_data_finished_handler

        for callback in self.callbacks.eis_data_end:
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

        for callback in self.callbacks.eis_data_start:
            _ = self.loop.call_soon_threadsafe(callback, data)  # type: ignore

    def comm_error_callback(self, sender: PalmSens.Comm.CommManager, args: System.EventArgs):
        """Called when a communication error occurs."""

        for callback in self.callbacks.comm_error:
            _ = self.loop.call_soon_threadsafe(callback)

        def teardown_and_raise():
            self.begin_measurement_event.set()
            self.end_measurement_event.set()

            raise ConnectionError('Measurement failed due to a communication or parsing error')

        _ = self.loop.call_soon_threadsafe(teardown_and_raise)
