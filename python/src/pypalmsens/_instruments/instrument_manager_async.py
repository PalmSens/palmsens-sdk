from __future__ import annotations

import asyncio
import sys
import traceback
from typing import Optional

import clr
import PalmSens
from PalmSens import AsyncEventHandler, Method, MuxModel
from PalmSens.Comm import CommManager, MuxType
from PalmSens.Plottables import (
    Curve,
    CurveEventHandler,
    EISData,
    EISDataEventHandler,
)
from System import EventHandler
from System.Threading.Tasks import Task

from .._data._shared import ArrayType, _get_values_from_NETArray
from .._methods import CURRENT_RANGE, MethodSettings
from ..data import Measurement
from ._common import Callback, Instrument, create_future, firmware_warning

WINDOWS = sys.platform == 'win32'
LINUX = not WINDOWS

if WINDOWS:
    from PalmSens.Windows.Devices import (
        BLEDevice,
        BluetoothDevice,
        FTDIDevice,
        USBCDCDevice,
    )

if LINUX:
    from PalmSens.Core.Linux.Comm.Devices import FTDIDevice, SerialPortDevice


async def discover_async(
    ftdi: bool = False,
    usbcdc: bool = True,
    bluetooth: bool = False,
    serial: bool = True,
) -> list[Instrument]:
    """Discover instruments.

    Parameters
    ----------
    ftdi : bool
        If True, discover ftdi devices
    usbcdc : bool
        If True, discover usbcdc devices (Windows only)
    bluetooth : bool
        If True, discover bluetooth devices (Windows only)
    """
    available_instruments = []

    if ftdi:
        ftdi_instruments = await create_future(FTDIDevice.DiscoverDevicesAsync())
        for ftdi_instrument in ftdi_instruments:
            instrument = Instrument(ftdi_instrument.ToString(), 'ftdi', ftdi_instrument)
            available_instruments.append(instrument)

    if LINUX:
        if serial:
            serial_instruments = await create_future(SerialPortDevice.DiscoverDevicesAsync())
            for serial_instrument in serial_instruments:
                instrument = Instrument(
                    serial_instrument.ToString(), 'serial', serial_instrument
                )
                available_instruments.append(instrument)

    if WINDOWS:
        if usbcdc:
            usbcdc_instruments = await create_future(USBCDCDevice.DiscoverDevicesAsync())
            for usbcdc_instrument in usbcdc_instruments:
                instrument = Instrument(
                    usbcdc_instrument.ToString(), 'usbcdc', usbcdc_instrument
                )
                available_instruments.append(instrument)

        if bluetooth:
            ble_instruments = await create_future(BLEDevice.DiscoverDevicesAsync())
            for ble_instrument in ble_instruments:
                instrument = Instrument(ble_instrument.ToString(), 'ble', ble_instrument)
                available_instruments.append(instrument)
            bluetooth_instruments = await create_future(BluetoothDevice.DiscoverDevicesAsync())
            for bluetooth_instrument in bluetooth_instruments[0]:
                instrument = Instrument(
                    bluetooth_instrument.ToString(), 'bluetooth', bluetooth_instrument
                )
                available_instruments.append(instrument)

    available_instruments.sort(key=lambda instrument: instrument.name)
    return available_instruments


async def connect_async(
    instrument: Optional[Instrument] = None,
) -> InstrumentManagerAsync:
    """Connect to instrument and return InstrumentManagerAsync.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to this instrument.
        If not specified, automatically discover and connect to the first instrument.

    Returns
    -------
    manager : InstrumentManagerAsync
        Return instance of `InstrumentManagerAsync` connected to the given instrument.
        The connection will be terminated after the context ends.
    """
    # connect to first device if not specified
    if not instrument:
        available_instruments = await discover_async()

        if not available_instruments:
            raise ConnectionError('No instruments were discovered.')

        # connect to first instrument
        instrument = available_instruments[0]

    manager = InstrumentManagerAsync(instrument)
    await manager.connect()
    return manager


class InstrumentManagerAsync:
    """Asynchronous instrument manager for PalmSens instruments.

    Parameters
    ----------
    instrument: Instrument
        Instrument to connect to, use `discover()` to find connected instruments.
    callback: Callback, optional
        If specified, call this function on every new set of data points.
        New data points are batched, and contain all points since the last
        time it was called. Each point is a dictionary containing
        `frequency`, `z_re`, `z_im` for impedimetric techniques and
        `index`, `x`, `x_unit`, `x_type`, `y`, `y_unit` and `y_type` for
        non-impedimetric techniques.
    """

    def __init__(self, instrument, *, callback: Optional[Callback] = None):
        self.callback = callback
        """This callback is called on every data point."""

        self.instrument = instrument
        """Instrument to connect to."""

        self.__comm = None
        self.__measuring = False
        self.__active_measurement = None
        self.__active_measurement_error = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.instrument.name})'

    async def __aenter__(self):
        if not self.is_connected():
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.disconnect()

    def is_connected(self) -> bool:
        """Return True if an instrument connection exists."""
        return self.__comm is not None

    async def connect(self):
        """Connect to instrument."""
        if self.__comm is not None:
            print(
                'An instance of the InstrumentManager can only be connected to one instrument at a time'
            )
            return 0

        try:
            __instrument = self.instrument.device
            await create_future(__instrument.OpenAsync())
            self.__comm = await create_future(CommManager.CommManagerAsync(__instrument))

            firmware_warning(self.__comm.Capabilities)

            return 1
        except Exception:
            traceback.print_exc()
            try:
                __instrument.Close()
            except Exception:
                pass
            return 0

    async def set_cell(self, cell_on: bool):
        """Turn the cell on or off.

        Parameters
        ----------
        cell_on : bool
            If true, turn on the cell
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(self.__comm.SetCellOnAsync(cell_on))
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def set_potential(self, potential: float):
        """Set the potential of the cell.

        Parameters
        ----------
        potential : float
            Potential in V
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(self.__comm.SetPotentialAsync(potential))
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def set_current_range(self, current_range: CURRENT_RANGE):
        """Set the current range for the cell.

        Parameters
        ----------
        current_range: CURRENT_RANGE
            Set the current range, use `pypalmsens.settings.CURRENT_RANGE`.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(self.__comm.SetCurrentRangeAsync(current_range._to_psobj()))
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def read_current(self) -> float:
        """Read the current in µA.

        Returns
        -------
        float
            Current in µA."
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            current = await create_future(self.__comm.GetCurrentAsync())  # in µA
            self.__comm.ClientConnection.Semaphore.Release()
            return current
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def read_potential(self) -> float:
        """Read the potential in V.

        Returns
        -------
        float
            Potential in V."""

        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            potential = await create_future(self.__comm.GetPotentialAsync())  # in V
            self.__comm.ClientConnection.Semaphore.Release()
            return potential
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def get_instrument_serial(self) -> str:
        """Return instrument serial number.

        Returns
        -------
        str
            Instrument serial.
        """
        if self.__comm is None:
            raise Exception('Not connected to an instrument')

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            serial = await create_future(self.__comm.GetDeviceSerialAsync())
            self.__comm.ClientConnection.Semaphore.Release()
            return serial.ToString()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def validate_method(self, psmethod):
        """Validate method."""
        if self.__comm is None:
            print('Not connected to an instrument')
            return False, None

        errors = psmethod.Validate(self.__comm.Capabilities)

        if any(error.IsFatal for error in errors):
            return False, 'Method not compatible:\n' + '\n'.join(
                [error.Message for error in errors]
            )

        return True, None

    async def measure(self, method: MethodSettings, hardware_sync_initiated_event=None):
        """Start measurement using given method parameters.

        Parameters
        ----------
        method: MethodParameters
            Method parameters for measurement
        hardware_sync_initiated_event:
            ...
        """
        psmethod = method._to_psmethod()
        if self.__comm is None:
            print('Not connected to an instrument')
            return None

        self.__active_measurement_error = None

        is_valid, message = self.validate_method(psmethod)
        if is_valid is not True:
            print(message)
            return None

        loop = asyncio.get_running_loop()
        begin_measurement_event = asyncio.Event()
        end_measurement_event = asyncio.Event()

        def begin_measurement(measurement):
            self.__active_measurement = measurement
            begin_measurement_event.set()

        def end_measurement():
            self.__measuring = False
            end_measurement_event.set()

        def curve_new_data_added(curve, start, count):
            data = []
            for i in range(start, start + count):
                point = {}
                point['index'] = i + 1
                point['x'] = _get_values_from_NETArray(curve.XAxisDataArray, start=i, count=1)[
                    0
                ]
                point['x_unit'] = curve.XUnit.ToString()
                point['x_type'] = ArrayType(curve.XAxisDataArray.ArrayType).name
                point['y'] = _get_values_from_NETArray(curve.YAxisDataArray, start=i, count=1)[
                    0
                ]
                point['y_unit'] = curve.YUnit.ToString()
                point['y_type'] = ArrayType(curve.YAxisDataArray.ArrayType).name
                data.append(point)
            self.callback(data)

        def eis_data_new_data_added(eis_data, start, count):
            data = []
            arrays = eis_data.EISDataSet.GetDataArrays()
            for i in range(start, start + count):
                point = {}
                point['index'] = i + 1
                for array in arrays:
                    array_type = ArrayType(array.ArrayType)
                    if array_type == ArrayType.Frequency:
                        point['frequency'] = _get_values_from_NETArray(array, start=i, count=1)[
                            0
                        ]
                    elif array_type == ArrayType.ZRe:
                        point['zre'] = _get_values_from_NETArray(array, start=i, count=1)[0]
                    elif array_type == ArrayType.ZIm:
                        point['zim'] = _get_values_from_NETArray(array, start=i, count=1)[0]
                data.append(point)
            self.callback(data)

        def comm_error():
            self.__measuring = False
            self.__active_measurement_error = (
                'measurement failed due to a communication or parsing error'
            )
            begin_measurement_event.set()
            end_measurement_event.set()

        def begin_measurement_callback(sender, args):
            loop.call_soon_threadsafe(lambda: begin_measurement(args.NewMeasurement))
            return Task.CompletedTask

        def end_measurement_callback(sender, args):
            loop.call_soon_threadsafe(end_measurement)
            return Task.CompletedTask

        def curve_data_added_callback(curve, args):
            start = args.StartIndex
            count = curve.NPoints - start
            future = asyncio.run_coroutine_threadsafe(
                curve_new_data_added_coroutine(curve, start, count), loop
            )
            future.result()  # block c# core library thread to apply backpressure and prevent unnescessary load on the python asyncio eventloop

        async def curve_new_data_added_coroutine(curve, start, count):
            curve_new_data_added(curve, start, count)

        def curve_finished_callback(curve, args):
            curve.NewDataAdded -= curve_data_added_handler
            curve.Finished -= curve_finished_handler

        def begin_receive_curve_callback(sender, args):
            curve = args.GetCurve()
            curve.NewDataAdded += curve_data_added_handler
            curve.Finished += curve_finished_handler

        def eis_data_data_added_callback(eis_data, args):
            start = args.Index
            count = 1
            loop.call_soon_threadsafe(lambda: eis_data_new_data_added(eis_data, start, count))

        def eis_data_finished_callback(eis_data, args):
            eis_data.NewDataAdded -= eis_data_data_added_handler
            eis_data.Finished -= eis_data_finished_handler

        def begin_receive_eis_data_callback(sender, eis_data):
            eis_data.NewDataAdded += eis_data_data_added_handler
            eis_data.Finished += eis_data_finished_handler

        def comm_error_callback(sender, args):
            loop.call_soon_threadsafe(comm_error)

        begin_measurement_handler = AsyncEventHandler[
            CommManager.BeginMeasurementEventArgsAsync
        ](begin_measurement_callback)
        end_measurement_handler = AsyncEventHandler[CommManager.EndMeasurementAsyncEventArgs](
            end_measurement_callback
        )
        begin_receive_curve_handler = CurveEventHandler(begin_receive_curve_callback)
        curve_data_added_handler = Curve.NewDataAddedEventHandler(curve_data_added_callback)
        curve_finished_handler = EventHandler(curve_finished_callback)
        eis_data_finished_handler = EventHandler(eis_data_finished_callback)
        begin_receive_eis_data_handler = EISDataEventHandler(begin_receive_eis_data_callback)
        eis_data_data_added_handler = EISData.NewDataEventHandler(eis_data_data_added_callback)
        comm_error_handler = EventHandler(comm_error_callback)

        # try:
        # subscribe to events indicating the start and end of the measurement
        self.__comm.BeginMeasurementAsync += begin_measurement_handler
        self.__comm.EndMeasurementAsync += end_measurement_handler
        self.__comm.Disconnected += comm_error_handler

        if self.callback is not None:
            self.__comm.BeginReceiveEISData += begin_receive_eis_data_handler
            self.__comm.BeginReceiveCurve += begin_receive_curve_handler

        # obtain lock on library (required when communicating with instrument)
        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        # send and execute the method on the instrument
        _ = await create_future(self.__comm.MeasureAsync(psmethod))
        self.__measuring = True

        # release lock on library (required when communicating with instrument)
        self.__comm.ClientConnection.Semaphore.Release()

        await begin_measurement_event.wait()

        if hardware_sync_initiated_event is not None:
            hardware_sync_initiated_event.set()

        await end_measurement_event.wait()

        # unsubscribe to events indicating the start and end of the measurement
        self.__comm.BeginMeasurementAsync -= begin_measurement_handler
        self.__comm.EndMeasurementAsync -= end_measurement_handler
        self.__comm.Disconnected -= comm_error_handler

        if self.callback is not None:
            self.__comm.BeginReceiveEISData -= begin_receive_eis_data_handler
            self.__comm.BeginReceiveCurve -= begin_receive_curve_handler

        if self.__active_measurement_error is not None:
            print(self.__active_measurement_error)
            return None

        measurement = self.__active_measurement
        self.__active_measurement = None
        return Measurement(psmeasurement=measurement)

        # except Exception:
        #     traceback.print_exc()

        #     if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
        #         # release lock on library (required when communicating with instrument)
        #         self.__comm.ClientConnection.Semaphore.Release()

        #     self.__active_measurement = None
        #     self.__comm.BeginMeasurementAsync -= begin_measurement_handler
        #     self.__comm.EndMeasurementAsync -= end_measurement_handler
        #     self.__comm.Disconnected -= comm_error_handler

        #     if self.new_data_callback is not None:
        #         self.__comm.BeginReceiveEISData -= begin_receive_eis_data_handler
        #         self.__comm.BeginReceiveCurve -= begin_receive_curve_handler

        #     self.__measuring = False
        #     return None

    def initiate_hardware_sync_follower_channel(self, method: MethodSettings):
        """Initiate hardware sync follower channel.

        Parameters
        ----------
        method : MethodParameters
            Method parameters
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        hardware_sync_channel_initiated_event = asyncio.Event()
        meaurement_finished_future = asyncio.Future()

        async def start_measurement(
            self, method, hardware_sync_channel_initiated_event, meaurement_finished_future
        ):
            measurement = await self.measure(
                method, hardware_sync_initiated_event=hardware_sync_channel_initiated_event
            )
            meaurement_finished_future.set_result(measurement)

        asyncio.run_coroutine_threadsafe(
            start_measurement(
                self, method, hardware_sync_channel_initiated_event, meaurement_finished_future
            ),
            asyncio.get_running_loop(),
        )

        return hardware_sync_channel_initiated_event.wait(), meaurement_finished_future

    async def wait_digital_trigger(self, wait_for_high):
        """Wait for digital trigger.

        Parameters
        ----------
        wait_for_high: ...
            ...
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        try:
            # obtain lock on library (required when communicating with instrument)
            await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

            while True:
                if await create_future(self.__comm.DigitalLineD0Async()) == wait_for_high:
                    break
                await asyncio.sleep(0.05)

            self.__comm.ClientConnection.Semaphore.Release()

        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def abort(self):
        """Abort measurement."""
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        if self.__measuring is False:
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(self.__comm.AbortAsync())
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def initialize_multiplexer(self, mux_model: int) -> int:
        """Initialize the multiplexer.

        Parameters
        ----------
        mux_model: int
            The model of the multiplexer. 0 = 8 channel, 1 = 16 channel, 2 = 32 channel.

        Returns
        -------
        int
            Number of available multiplexes channels
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            model = MuxModel(mux_model)

            if model == MuxModel.MUX8R2 and (
                self.__comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionPS4)
                )
                or self.__comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionMS)
                )
            ):
                await create_future(self.__comm.ClientConnection.ReadMuxInfoAsync())

            self.__comm.Capabilities.MuxModel = model

            if self.__comm.Capabilities.MuxModel == MuxModel.MUX8:
                self.__comm.Capabilities.NumMuxChannels = 8
            elif self.__comm.Capabilities.MuxModel == MuxModel.MUX16:
                self.__comm.Capabilities.NumMuxChannels = 16
            elif self.__comm.Capabilities.MuxModel == MuxModel.MUX8R2:
                await create_future(self.__comm.ClientConnection.ReadMuxInfoAsync())

            self.__comm.ClientConnection.Semaphore.Release()

            return self.__comm.Capabilities.NumMuxChannels
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

            raise Exception(
                'Failed to read MUX info. Please check the connection, restart the instrument and try again.'
            )

    async def set_mux8r2_settings(
        self,
        connect_sense_to_working_electrode: bool = False,
        combine_reference_and_counter_electrodes: bool = False,
        use_channel_1_reference_and_counter_electrodes: bool = False,
        set_unselected_channel_working_electrode: int = 0,
    ):
        """Set the settings for the Mux8R2 multiplexer.

        Parameters
        ---------
        connect_sense_to_working_electrode: float
            Connect the sense electrode to the working electrode. Default is False.
        combine_reference_and_counter_electrodes: float
            Combine the reference and counter electrodes. Default is False.
        use_channel_1_reference_and_counter_electrodes: float
            Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
        set_unselected_channel_working_electrode: float
            Set the unselected channel working electrode to disconnected/floating (0), ground (1), or standby potential (2). Default is 0.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return

        if self.__comm.Capabilities.MuxModel != MuxModel.MUX8R2:
            return

        mux_settings = Method.MuxSettings(False)
        mux_settings.ConnSEWE = connect_sense_to_working_electrode
        mux_settings.ConnectCERE = combine_reference_and_counter_electrodes
        mux_settings.CommonCERE = use_channel_1_reference_and_counter_electrodes
        mux_settings.UnselWE = Method.MuxSettings.UnselWESetting(
            set_unselected_channel_working_electrode
        )

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(
                self.__comm.ClientConnection.SetMuxSettingsAsync(MuxType(1), mux_settings)
            )
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def set_multiplexer_channel(self, channel: int):
        """Sets the multiplexer channel.

        Parameters
        ----------
        channel : int
            Index of the channel to set.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(self.__comm.ClientConnection.SetMuxChannelAsync(channel))
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def disconnect(self):
        """Disconnect from the instrument."""
        if self.__comm is None:
            return 0
        try:
            await create_future(self.__comm.DisconnectAsync())
            self.__comm = None
            self.__measuring = False
            return 1
        except Exception:
            traceback.print_exc()
            return 0
