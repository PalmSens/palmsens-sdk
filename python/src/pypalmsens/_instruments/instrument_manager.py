from __future__ import annotations

import asyncio
import sys
import traceback
from time import sleep
from typing import Optional

import clr
import PalmSens
from PalmSens import Method, MuxModel
from PalmSens.Comm import CommManager, MuxType
from PalmSens.Plottables import (
    Curve,
    CurveEventHandler,
    EISData,
    EISDataEventHandler,
)
from System import EventHandler  # type: ignore

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
else:
    from PalmSens.Core.Linux.Comm.Devices import FTDIDevice, SerialPortDevice


def discover(
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
    serial : bool
        If True, discover serial devices
    """
    available_instruments = []

    args = [''] if WINDOWS else []

    if ftdi:
        ftdi_instruments = FTDIDevice.DiscoverDevices(*args)
        for ftdi_instrument in ftdi_instruments[0]:
            instrument = Instrument(ftdi_instrument.ToString(), 'ftdi', ftdi_instrument)
            available_instruments.append(instrument)

    if WINDOWS and usbcdc:
        usbcdc_instruments = USBCDCDevice.DiscoverDevices(*args)
        for usbcdc_instrument in usbcdc_instruments[0]:
            instrument = Instrument(usbcdc_instrument.ToString(), 'usbcdc', usbcdc_instrument)
            available_instruments.append(instrument)

    if WINDOWS and bluetooth:
        ble_instruments = BLEDevice.DiscoverDevices(*args)
        for ble_instrument in ble_instruments[0]:
            instrument = Instrument(ble_instrument.ToString(), 'ble', ble_instrument)
            available_instruments.append(instrument)
        bluetooth_instruments = BluetoothDevice.DiscoverDevices(*args)
        for bluetooth_instrument in bluetooth_instruments[0]:
            instrument = Instrument(
                bluetooth_instrument.ToString(), 'bluetooth', bluetooth_instrument
            )
            available_instruments.append(instrument)

    if LINUX and serial:
        serial_instruments = SerialPortDevice.DiscoverDevices(*args)
        for serial_instrument in serial_instruments:
            instrument = Instrument(serial_instrument.ToString(), 'serial', serial_instrument)
            available_instruments.append(instrument)

    available_instruments.sort(key=lambda instrument: instrument.name)
    return available_instruments


def connect(
    instrument: Optional[Instrument] = None,
) -> InstrumentManager:
    """Connect to instrument and return InstrumentManager.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to this instrument.
        If not specified, automatically discover and connect to the first instrument.

    Returns
    -------
    manager : InstrumentManager
        Return instance of `InstrumentManager` connected to the given instrument.
        The connection will be terminated after the context ends.
    """
    # connect to first device if not specified
    if not instrument:
        available_instruments = discover()

        if not available_instruments:
            raise ConnectionError('No instruments were discovered.')

        # connect to first instrument
        instrument = available_instruments[0]

    manager = InstrumentManager(instrument)
    manager.connect()
    return manager


class InstrumentManager:
    """Instrument manager for PalmSens instruments.

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

    def __init__(self, instrument: Instrument, *, callback: Optional[Callback] = None):
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

    def __enter__(self):
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def is_connected(self) -> bool:
        """Return True if an instrument connection exists."""
        return self.__comm is not None

    def connect(self):
        """Connect to instrument."""
        if self.__comm is not None:
            print(
                'An instance of the InstrumentManager can only be connected to one instrument at a time'
            )
            return 0
        try:
            __instrument = self.instrument.device
            __instrument.Open()
            self.__comm = CommManager(__instrument)

            firmware_warning(self.__comm.Capabilities)

            return 1
        except Exception:
            traceback.print_exc()
            try:
                __instrument.Close()
            except Exception:
                pass
            return 0

    def set_cell(self, cell_on: bool):
        """Turn the cell on or off.

        Parameters
        ----------
        cell_on : bool
            If true, turn on the cell
        """
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

    def set_potential(self, potential: float):
        """Set the potential of the cell.

        Parameters
        ----------
        potential : float
            Potential in V
        """
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

    def set_current_range(self, current_range: CURRENT_RANGE):
        """Set the current range for the cell.

        Parameters
        ----------
        current_range: CURRENT_RANGE
            Set the current range, use `pypalmsens.settings.CURRENT_RANGE`.
        """
        if self.__comm is None:
            print('Not connected to an instrument')
            return 0

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self.__comm.CurrentRange = current_range._to_psobj()
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def read_current(self) -> float:
        """Read the current in µA.

        Returns
        -------
        float
            Current in µA."
        """
        if self.__comm is None:
            raise ConnectionError('Not connected to an instrument')

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

    def read_potential(self) -> float:
        """Read the potential in V.

        Returns
        -------
        float
            Potential in V."""

        if self.__comm is None:
            raise ConnectionError('Not connected to an instrument')

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

    def get_instrument_serial(self) -> str:
        """Return instrument serial number.

        Returns
        -------
        str
            Instrument serial.
        """
        if self.__comm is None:
            raise ConnectionError('Not connected to an instrument')

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

    def measure(self, method: MethodSettings):
        """Start measurement using given method parameters.

        Parameters
        ----------
        method: MethodParameters
            Method parameters for measurement
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

        loop = asyncio.new_event_loop()
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

            if self.callback is not None:
                self.__comm.BeginReceiveEISData += begin_receive_eis_data_handler
                self.__comm.BeginReceiveCurve += begin_receive_curve_handler

            async def await_measurement():
                # obtain lock on library (required when communicating with instrument)
                await create_future(self.__comm.ClientConnection.Semaphore.WaitAsync())

                # send and execute the method on the instrument
                _ = self.__comm.Measure(psmethod)
                self.__measuring = True

                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

                await begin_measurement_event.wait()
                await end_measurement_event.wait()

            loop.run_until_complete(await_measurement())
            loop.close()

            # unsubscribe to events indicating the start and end of the measurement
            self.__comm.BeginMeasurement -= begin_measurement_handler
            self.__comm.EndMeasurement -= end_measurement_handler
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

        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

            self.__active_measurement = None
            self.__comm.BeginMeasurement -= begin_measurement_handler
            self.__comm.EndMeasurement -= end_measurement_handler
            self.__comm.Disconnected -= comm_error_handler

            if self.callback is not None:
                self.__comm.BeginReceiveEISData -= begin_receive_eis_data_handler
                self.__comm.BeginReceiveCurve -= begin_receive_curve_handler

            self.__measuring = False
            return None

    def wait_digital_trigger(self, wait_for_high):
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
        """Abort measurement."""
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

    def initialize_multiplexer(self, mux_model: int) -> int:
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

    def set_mux8r2_settings(
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

        self.__comm.ClientConnection.Semaphore.Wait()

        try:
            self.__comm.ClientConnection.SetMuxSettings(MuxType(1), mux_settings)
            self.__comm.ClientConnection.Semaphore.Release()
        except Exception:
            traceback.print_exc()

            if self.__comm.ClientConnection.Semaphore.CurrentCount == 0:
                # release lock on library (required when communicating with instrument)
                self.__comm.ClientConnection.Semaphore.Release()

    def set_multiplexer_channel(self, channel: int):
        """Sets the multiplexer channel.

        Parameters
        ----------
        channel : int
            Index of the channel to set.
        """
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
        """Disconnect from the instrument."""
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
