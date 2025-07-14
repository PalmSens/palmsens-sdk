import asyncio
import traceback
from time import sleep

import clr
import PalmSens  # type: ignore
from PalmSens import AsyncEventHandler, MuxModel  # type: ignore
from PalmSens.Comm import CommManager, MuxType  # type: ignore
from PalmSens.Plottables import (  # type: ignore
    Curve,
    CurveEventHandler,
    EISData,
    EISDataEventHandler,
)
from PalmSens.Windows.Devices import (  # type: ignore
    BLEDevice,
    BluetoothDevice,
    FTDIDevice,
    USBCDCDevice,
)
from System import Action, EventHandler  # type: ignore
from System.Threading.Tasks import Task  # type: ignore

from .data._shared import ArrayType, _get_values_from_NETArray
from .data.measurement import Measurement
from .pspymethods import get_mux8r2_settings


def create_future(clr_task):
    loop = asyncio.get_running_loop()
    future = asyncio.Future()
    callback = Action(lambda: on_completion(future, loop, clr_task))

    clr_task.GetAwaiter().OnCompleted(callback)
    return future


def on_completion(future, loop, task):
    if task.IsFaulted:
        clr_error = task.Exception.GetBaseException()
        future.set_exception(clr_error)
    else:
        loop.call_soon_threadsafe(lambda: future.set_result(task.GetAwaiter().GetResult()))


def discover_instruments(**kwargs):
    discover_ftdi = kwargs.get('ftdi', True)
    discover_usbcdc = kwargs.get('usbcdc', True)
    discover_bluetooth = kwargs.get('bluetooth', False)
    available_instruments = []

    if discover_ftdi:
        ftdi_instruments = FTDIDevice.DiscoverDevices('')
        for ftdi_instrument in ftdi_instruments[0]:
            instrument = Instrument(ftdi_instrument.ToString(), 'ftdi', ftdi_instrument)
            available_instruments.append(instrument)

    if discover_usbcdc:
        usbcdc_instruments = USBCDCDevice.DiscoverDevices('')
        for usbcdc_instrument in usbcdc_instruments[0]:
            instrument = Instrument(usbcdc_instrument.ToString(), 'usbcdc', usbcdc_instrument)
            available_instruments.append(instrument)

    if discover_bluetooth:
        ble_instruments = BLEDevice.DiscoverDevices('')
        for ble_instrument in ble_instruments[0]:
            instrument = Instrument(ble_instrument.ToString(), 'ble', ble_instrument)
            available_instruments.append(instrument)
        bluetooth_instruments = BluetoothDevice.DiscoverDevices('')
        for bluetooth_instrument in bluetooth_instruments[0]:
            instrument = Instrument(
                bluetooth_instrument.ToString(), 'bluetooth', bluetooth_instrument
            )
            available_instruments.append(instrument)

    available_instruments.sort(key=lambda instrument: instrument.name)
    return available_instruments


async def discover_instruments_async(**kwargs):
    discover_ftdi = kwargs.get('ftdi', True)
    discover_usbcdc = kwargs.get('usbcdc', True)
    discover_bluetooth = kwargs.get('bluetooth', False)
    available_instruments = []

    if discover_ftdi:
        ftdi_instruments = await create_future(FTDIDevice.DiscoverDevicesAsync())
        for ftdi_instrument in ftdi_instruments:
            instrument = Instrument(ftdi_instrument.ToString(), 'ftdi', ftdi_instrument)
            available_instruments.append(instrument)

    if discover_usbcdc:
        usbcdc_instruments = await create_future(USBCDCDevice.DiscoverDevicesAsync())
        for usbcdc_instrument in usbcdc_instruments:
            instrument = Instrument(usbcdc_instrument.ToString(), 'usbcdc', usbcdc_instrument)
            available_instruments.append(instrument)

    if discover_bluetooth:
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


class Instrument:
    def __init__(self, name, conn, device):
        self.name = name
        self.connection = conn
        self.device = device


class InstrumentManager:
    def __init__(self, **kwargs):
        self.new_data_callback = kwargs.get('new_data_callback', None)
        self.__comm = None
        self.__measuring = False
        self.__active_measurement = None
        self.__active_measurement_error = None

    def connect(self, instrument):
        if self.__comm is not None:
            print(
                'An instance of the InstrumentManager can only be connected to one instrument at a time'
            )
            return 0
        try:
            __instrument = instrument.device
            __instrument.Open()
            self.__comm = CommManager(__instrument)
            return 1
        except Exception:
            traceback.print_exc()
            try:
                __instrument.Close()
            except Exception:
                pass
            return 0

    def set_cell(self, cell_on):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self.__comm.CellOn = cell_on
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def set_potential(self, potential):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self.__comm.Potential = potential
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def set_current_range(self, current_range):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self.__comm.CurrentRange = current_range
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def read_current(self):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            current = self.__comm.Current  # in µA
            self.__comm.ClientConnection.Semaphore.Release()
            return current
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def read_potential(self):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            potential = self.__comm.Potential  # in V
            self.__comm.ClientConnection.Semaphore.Release()
            return potential
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def get_instrument_serial(self):
        if self.__comm is None:
            raise Exception('Not connected to an instrument')

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            serial = self.__comm.DeviceSerial.ToString()
            self.__comm.ClientConnection.Semaphore.Release()
            return serial
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def validate_method(self, method):
        if self.__comm is None:
            print('Not connected to an instrument')
            return False, None

        errors = method.Validate(self.__comm.Capabilities)

        if any(error.IsFatal for error in errors):
            return False, 'Method not compatible:\n' + '\n'.join(
                [error.Message for error in errors]
            )

        return True, None

    def measure(self, method):
        if self.__comm is None:
            print('Not connected to an instrument')
            return None

        self.__active_measurement_error = None

        is_valid, message = self.validate_method(method)
        if is_valid is not True:
            print(message)
            return None

        loop = asyncio.get_event_loop()
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
            self.new_data_callback(data)

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
            self.new_data_callback(data)

        def comm_error():
            self.__measuring = False
            self.__active_measurement_error = (
                'measurement failed due to a communication or parsing error'
            )
            begin_measurement_event.set()
            end_measurement_event.set()

        def begin_measurement_callback(sender, measurement):
            loop.call_soon_threadsafe(lambda: begin_measurement(measurement))

        def end_measurement_callback(sender, args):
            loop.call_soon_threadsafe(end_measurement)

        def curve_data_added_callback(curve, args):
            start = args.StartIndex
            count = curve.NPoints - start
            loop.call_soon_threadsafe(lambda: curve_new_data_added(curve, start, count))

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

        begin_measurement_handler = CommManager.BeginMeasurementEventHandler(
            begin_measurement_callback
        )
        end_measurement_handler = EventHandler(end_measurement_callback)
        begin_receive_curve_handler = CurveEventHandler(begin_receive_curve_callback)
        curve_data_added_handler = Curve.NewDataAddedEventHandler(curve_data_added_callback)
        curve_finished_handler = EventHandler(curve_finished_callback)
        eis_data_finished_handler = EventHandler(eis_data_finished_callback)
        begin_receive_eis_data_handler = EISDataEventHandler(begin_receive_eis_data_callback)
        eis_data_data_added_handler = EISData.NewDataEventHandler(eis_data_data_added_callback)
        comm_error_handler = EventHandler(comm_error_callback)

        try:
            # subscribe to events indicating the start and end of the measurement
            self.__comm.BeginMeasurement += begin_measurement_handler
            self.__comm.EndMeasurement += end_measurement_handler
            self.__comm.Disconnected += comm_error_handler

            if self.new_data_callback is not None:
                self.__comm.BeginReceiveEISData += begin_receive_eis_data_handler
                self.__comm.BeginReceiveCurve += begin_receive_curve_handler

            async def await_measurement():
                # obtain lock on library (required when communicating with instrument)
                await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

                # send and execute the method on the instrument
                _ = self.__comm.Measure(method)
                self.__measuring = True

                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

                await begin_measurement_event.wait()
                await end_measurement_event.wait()

            loop.run_until_complete(await_measurement())

            # unsubscribe to events indicating the start and end of the measurement
            self.__comm.BeginMeasurement -= begin_measurement_handler
            self.__comm.EndMeasurement -= end_measurement_handler
            self.__comm.Disconnected -= comm_error_handler

            if self.new_data_callback is not None:
                self.__comm.BeginReceiveEISData -= begin_receive_eis_data_handler
                self.__comm.BeginReceiveCurve -= begin_receive_curve_handler

            if self.__active_measurement_error is not None:
                print(self.__active_measurement_error)
                return None

            measurement = self.__active_measurement
            self.__active_measurement = None
            return Measurement(dotnet_measurement=measurement)

        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

            self.__active_measurement = None
            self.__comm.BeginMeasurement -= begin_measurement_handler
            self.__comm.EndMeasurement -= end_measurement_handler
            self.__comm.Disconnected -= comm_error_handler

            if self.new_data_callback is not None:
                self.__comm.BeginReceiveEISData -= begin_receive_eis_data_handler
                self.__comm.BeginReceiveCurve -= begin_receive_curve_handler

            self.__measuring = False
            return None

    def wait_digital_trigger(self, wait_for_high):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        try:
            # obtain lock on library (required when communicating with instrument)
            self.__comm.ClientConnection.Semaphore.Wait()

            while True:
                if self.__comm.DigitalLineD0 == wait_for_high:
                    break
                sleep(0.05)

            self.__comm.ClientConnection.Semaphore.Release()

        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def abort(self):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        if self.__measuring is False:
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()
        try:
            self.__comm.Abort()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def initialize_multiplexer(self, mux_model):
        """Initialize the multiplexer. Returns the number of available multiplexer
        channels.

        :param mux_model: The model of the multiplexer. 0 = 8 channel, 1 = 16 channel, 2
            = 32 channel.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

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
                self.__comm.ClientConnection.ReadMuxInfo()

            self.__comm.Capabilities.MuxModel = model

            if self.__comm.Capabilities.MuxModel == MuxModel.MUX8:
                self.__comm.Capabilities.NumMuxChannels = 8
            elif self.__comm.Capabilities.MuxModel == MuxModel.MUX16:
                self.__comm.Capabilities.NumMuxChannels = 16
            elif self.__comm.Capabilities.MuxModel == MuxModel.MUX8R2:
                self.__comm.ClientConnection.ReadMuxInfo()

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

    def set_mux8r2_settings(self, **kwargs):
        """Set the settings for the Mux8R2 multiplexer.

        :Keyword Arguments:
        * connect_sense_to_working_electrode
            -- Connect the sense electrode to the working electrode. Default is False.
        * combine_reference_and_counter_electrodes
            -- Combine the reference and counter electrodes. Default is False.
        * use_channel_1_reference_and_counter_electrodes
            -- Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
        * set_unselected_channel_working_electrode
            -- Set the unselected channel working electrode to disconnected/floating (0), ground (1), or standby potential (2). Default is 0.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return

        if self.__comm.Capabilities.MuxModel != MuxModel.MUX8R2:
            return

        mux_settings = get_mux8r2_settings(
            connect_sense_to_working_electrode=kwargs.get(
                'connect_sense_to_working_electrode', False
            ),
            combine_reference_and_counter_electrodes=kwargs.get(
                'combine_reference_and_counter_electrodes', False
            ),
            use_channel_1_reference_and_counter_electrodes=kwargs.get(
                'use_channel_1_reference_and_counter_electrodes', False
            ),
            set_unselected_channel_working_electrode=kwargs.get(
                'set_unselected_channel_working_electrode', 0
            ),
        )

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self._InstrumentManager__comm.ClientConnection.SetMuxSettings(
                MuxType(1), mux_settings
            )
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def set_multiplexer_channel(self, channel):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self.__comm.ClientConnection.SetMuxChannel(channel)
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def disconnect(self):
        if self.__comm is None:
            return 0
        try:
            self.__comm.Disconnect()
            self.__comm = None
            self.__measuring = False
            return 1
        except Exception:
            traceback.print_exc()
            return 0


class InstrumentManagerAsync:
    def __init__(self, **kwargs):
        self.new_data_callback = kwargs.get('new_data_callback', None)
        self.__comm = None
        self.__measuring = False
        self.__active_measurement = None
        self.__active_measurement_error = None

    async def connect(self, instrument):
        if self.__comm is not None:
            print(
                'An instance of the InstrumentManager can only be connected to one instrument at a time'
            )
            return 0
        try:
            __instrument = instrument.device
            await create_future(__instrument.OpenAsync())
            self.__comm = await create_future(CommManager.CommManagerAsync(__instrument))
            return 1
        except Exception:
            traceback.print_exc()
            try:
                __instrument.Close()
            except Exception:
                pass
            return 0

    async def set_cell(self, cell_on):
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

    async def set_potential(self, potential):
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

    async def set_current_range(self, current_range):
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(self.__comm.SetCurrentRangeAsync(current_range))
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def read_current(self):
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

    async def read_potential(self):
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

    async def get_instrument_serial(self):
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

    def validate_method(self, method):
        if self.__comm is None:
            print('Not connected to an instrument')
            return False, None

        errors = method.Validate(self.__comm.Capabilities)

        if any(error.IsFatal for error in errors):
            return False, 'Method not compatible:\n' + '\n'.join(
                [error.Message for error in errors]
            )

        return True, None

    async def measure(self, method, hardware_sync_initiated_event=None):
        if self.__comm is None:
            print('Not connected to an instrument')
            return None

        self.__active_measurement_error = None

        is_valid, message = self.validate_method(method)
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
            self.new_data_callback(data)

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
            self.new_data_callback(data)

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

        if self.new_data_callback is not None:
            self.__comm.BeginReceiveEISData += begin_receive_eis_data_handler
            self.__comm.BeginReceiveCurve += begin_receive_curve_handler

        # obtain lock on library (required when communicating with instrument)
        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        # send and execute the method on the instrument
        _ = await create_future(self.__comm.MeasureAsync(method))
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

        if self.new_data_callback is not None:
            self.__comm.BeginReceiveEISData -= begin_receive_eis_data_handler
            self.__comm.BeginReceiveCurve -= begin_receive_curve_handler

        if self.__active_measurement_error is not None:
            print(self.__active_measurement_error)
            return None

        measurement = self.__active_measurement
        self.__active_measurement = None
        return Measurement(dotnet_measurement=measurement)

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

    def initiate_hardware_sync_follower_channel(self, method):
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

    async def initialize_multiplexer(self, mux_model):
        """Initialize the multiplexer. Returns the number of available multiplexer
        channels.

        :param mux_model: The model of the multiplexer. 0 = 8 channel, 1 = 16 channel, 2
            = 32 channel.
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

    async def set_mux8r2_settings(self, **kwargs):
        """Set the settings for the Mux8R2 multiplexer.

        :Keyword Arguments:
        * connect_sense_to_working_electrode
            -- Connect the sense electrode to the working electrode. Default is False.
        * combine_reference_and_counter_electrodes
            -- Combine the reference and counter electrodes. Default is False.
        * use_channel_1_reference_and_counter_electrodes
            -- Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
        * set_unselected_channel_working_electrode
            -- Set the unselected channel working electrode to disconnected/floating (0), ground (1), or standby potential (2). Default is 0.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return

        if self.__comm.Capabilities.MuxModel != MuxModel.MUX8R2:
            return

        mux_settings = get_mux8r2_settings(
            connect_sense_to_working_electrode=kwargs.get(
                'connect_sense_to_working_electrode', False
            ),
            combine_reference_and_counter_electrodes=kwargs.get(
                'combine_reference_and_counter_electrodes', False
            ),
            use_channel_1_reference_and_counter_electrodes=kwargs.get(
                'use_channel_1_reference_and_counter_electrodes', False
            ),
            set_unselected_channel_working_electrode=kwargs.get(
                'set_unselected_channel_working_electrode', 0
            ),
        )

        await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

        try:
            await create_future(
                self._InstrumentManager__comm.ClientConnection.SetMuxSettingsAsync(
                    MuxType(1), mux_settings
                )
            )
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    async def set_multiplexer_channel(self, channel):
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
