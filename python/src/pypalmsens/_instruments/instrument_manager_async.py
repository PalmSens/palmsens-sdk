from __future__ import annotations

import asyncio
import sys
import warnings
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Coroutine

import clr
import PalmSens
import System
from PalmSens import Method as PSMethod
from PalmSens import MuxModel
from PalmSens.Comm import CommManager, MuxType
from typing_extensions import AsyncIterator, override

from .._methods import (
    AllowedCurrentRanges,
    BaseTechnique,
    cr_string_to_enum,
)
from ..data import Measurement
from ._common import Callback, Instrument, create_future, firmware_warning
from .measurement_manager_async import MeasurementManagerAsync

WINDOWS = sys.platform == 'win32'
LINUX = not WINDOWS

if WINDOWS:
    from PalmSens.Windows.Devices import (
        BLEDevice,
        BluetoothDevice,
        FTDIDevice,
        USBCDCDevice,
        WinUSBDevice,
    )
else:
    from PalmSens.Core.Linux.Comm.Devices import FTDIDevice, SerialPortDevice


if TYPE_CHECKING:
    from PalmSens import Method as PSMethod

warnings.simplefilter('default')


async def discover_async(
    ftdi: bool = True,
    usbcdc: bool = True,
    winusb: bool = True,
    bluetooth: bool = False,
    serial: bool = True,
    ignore_errors: bool = False,
) -> list[Instrument]:
    """Discover instruments.

    For a list of device interfaces, see:
        https://sdk.palmsens.com/python/latest/installation.html#compatibility

    Parameters
    ----------
    ftdi : bool
        If True, discover ftdi devices
    usbcdc : bool
        If True, discover usbcdc devices (Windows only)
    winusb : bool
        If True, discover winusb devices (Windows only)
    bluetooth : bool
        If True, discover bluetooth devices (Windows only)
    serial : bool
        If True, discover serial devices
    ignore_errors : False
        Ignores errors in device discovery

    Returns
    -------
    discovered : list[Instrument]
        List of dataclasses with discovered instruments.
    """
    interfaces: dict[str, Any] = {}

    if ftdi:
        interfaces['ftdi'] = FTDIDevice

    if WINDOWS:
        if usbcdc:
            interfaces['usbcdc'] = USBCDCDevice

        if winusb:
            interfaces['winusb'] = WinUSBDevice

        if bluetooth:
            interfaces['bluetooth'] = BluetoothDevice
            interfaces['ble'] = BLEDevice

    if LINUX:
        if serial:
            interfaces['serial'] = SerialPortDevice

    instruments: list[Instrument] = []

    for name, interface in interfaces.items():
        try:
            devices: list[PalmSens.Devices.Device] = await create_future(
                interface.DiscoverDevicesAsync()
            )
        except System.DllNotFoundException:
            if ignore_errors:
                continue

            if name == 'ftdi':
                msg = (
                    'Cannot discover FTDI devices (missing driver).'
                    '\nfor more information see: '
                    'https://sdk.palmsens.com/python/latest/installation.html#ftdisetup'
                    '\nSet `ftdi=False` to hide this message.'
                )
                warnings.warn(msg, stacklevel=2)
                continue
            raise

        for device in devices:
            instruments.append(
                Instrument(
                    id=device.ToString(),
                    interface=name,
                    device=device,
                )
            )

    instruments.sort(key=lambda instrument: instrument.id)

    return instruments


async def connect_async(
    instrument: None | Instrument = None,
) -> InstrumentManagerAsync:
    """Async connect to instrument and return `InstrumentManagerAsync`.

    Connects to any plugged-in PalmSens USB device.
    Error if multiple devices are plugged-in.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to a specific instrument.
        Use `pypalmsens.discover_async()` to discover instruments.

    Returns
    -------
    manager : InstrumentManagerAsync
        Return instance of `InstrumentManagerAsync` connected to the given instrument.
    """
    if not instrument:
        available_instruments = await discover_async(ignore_errors=True)

        if not available_instruments:
            raise ConnectionError('No instruments were discovered.')

        if len(available_instruments) > 1:
            raise ConnectionError('More than one device discovered.')

        instrument = available_instruments[0]

    manager = InstrumentManagerAsync(instrument)
    await manager.connect()
    return manager


async def measure_async(
    method: BaseTechnique,
    instrument: None | Instrument = None,
    callback: Callback | None = None,
) -> Measurement:
    """Run measurement async.

    Executes the given method on any plugged-in PalmSens USB device.
    Error if multiple devices are plugged-in.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to and meassure on a specific instrument.
        Use `pypalmsens.discover_async()` to discover instruments.
    callback: Callback, optional
        If specified, call this function on every new set of data points.
        New data points are batched, and contain all points since the last
        time it was called. Each point is a dictionary containing
        `frequency`, `z_re`, `z_im` for impedimetric techniques and
        `index`, `x`, `x_unit`, `x_type`, `y`, `y_unit` and `y_type` for
        non-impedimetric techniques.

    Returns
    -------
    measurement : Measurement
        Finished measurement.
    """
    async with await connect_async(instrument=instrument) as manager:
        measurement = await manager.measure(method, callback=callback)

    assert measurement

    return measurement


class InstrumentManagerAsync:
    """Asynchronous instrument manager for PalmSens instruments.

    Parameters
    ----------
    instrument: Instrument
        Instrument to connect to, use `discover()` to find connected instruments.
    callback : Callback, optional
        Deprecated. Pass your callback to `InstrumentManagerAsync.measure()` directly instead.
    """

    def __init__(self, instrument: Instrument, *, callback: None | Callback = None):
        if callback:
            warnings.warn(
                (
                    'Passing a callback to the instrument manager is '
                    'deprecated and will be removed in a future version. '
                    'Use `InstrumentManager.measure(..., callback=callback)` '
                    'instead.'
                ),
                DeprecationWarning,
            )

        self.callback: None | Callback = callback
        """This callback is called on every data point."""

        self.instrument: Instrument = instrument
        """Instrument to connect to."""

        self._comm: CommManager

    @override
    def __repr__(self):
        return (
            f'{self.__class__.__name__}({self.instrument.id}, connected={self.is_connected()})'
        )

    async def __aenter__(self):
        if not self.is_connected():
            _ = await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        _ = await self.disconnect()

    def is_measuring(self) -> bool:
        """Return True if device is measuring."""
        return int(self._comm.State) == CommManager.DeviceState.Measurement

    @asynccontextmanager
    async def _lock(self) -> AsyncIterator[CommManager]:
        self.ensure_connection()

        await create_future(self._comm.ClientConnection.Semaphore.WaitAsync())

        try:
            yield self._comm

        except Exception:
            raise

        finally:
            if self._comm.ClientConnection.Semaphore.CurrentCount == 0:
                _ = self._comm.ClientConnection.Semaphore.Release()

    def is_connected(self) -> bool:
        """Return True if an instrument connection exists."""
        try:
            self._comm
        except AttributeError:
            return False
        else:
            return True

    def ensure_connection(self):
        """Raises connection error if the instrument is not connected."""
        if not self.is_connected():
            raise ConnectionError('Not connected to an instrument')

    async def connect(self) -> None:
        """Connect to instrument."""
        if self.is_connected():
            return

        psinstrument = self.instrument.device
        try:
            await create_future(psinstrument.OpenAsync())
        except System.UnauthorizedAccessException as err:
            raise ConnectionError(
                f'Cannot open instrument connection (reason: {err.Message}). Check if the device is already in use.'
            ) from err

        self._comm = await create_future(CommManager.CommManagerAsync(psinstrument))

        firmware_warning(self._comm.Capabilities)

    async def set_cell(self, cell_on: bool) -> None:
        """Turn the cell on or off.

        Parameters
        ----------
        cell_on : bool
            If true, turn on the cell
        """
        async with self._lock():
            await create_future(self._comm.SetCellOnAsync(cell_on))

    async def set_potential(self, potential: float) -> None:
        """Set the potential of the cell.

        Parameters
        ----------
        potential : float
            Potential in V
        """
        async with self._lock():
            await create_future(self._comm.SetPotentialAsync(potential))

    async def set_current_range(self, current_range: AllowedCurrentRanges):
        """Set the current range for the cell.

        Parameters
        ----------
        current_range: AllowedCurrentRanges
            Set the current range as a string.
            See `pypalmsens.settings.AllowedCurrentRanges` for options.
        """
        async with self._lock():
            await create_future(
                self._comm.SetCurrentRangeAsync(cr_string_to_enum(current_range))
            )

    async def read_current(self) -> float:
        """Read the current in µA.

        Returns
        -------
        current : float
            Current in µA.
        """
        async with self._lock():
            current: float = await create_future(self._comm.GetCurrentAsync())

        return current

    async def read_potential(self) -> float:
        """Read the potential in V.

        Returns
        -------
        potential : float
            Potential in V.
        """

        async with self._lock():
            potential: float = await create_future(self._comm.GetPotentialAsync())

        return potential

    async def get_instrument_serial(self) -> str:
        """Return instrument serial number.

        Returns
        -------
        serial : str
            Instrument serial.
        """
        async with self._lock():
            serial: PalmSens.Comm.DeviceSerialV3 = await create_future(
                self._comm.GetDeviceSerialAsync()
            )

        return serial.ToString()

    def validate_method(self, method: PSMethod | BaseTechnique) -> None:
        """Validate method.

        Raise ValueError if the method cannot be validated."""
        self.ensure_connection()

        if not isinstance(method, PSMethod):
            method = method._to_psmethod()

        errors = method.Validate(self._comm.Capabilities)

        if any(error.IsFatal for error in errors):
            message = '\n'.join([error.Message for error in errors])
            raise ValueError(f'Method not compatible:\n{message}')

    async def measure(
        self,
        method: BaseTechnique,
        *,
        callback: Callback | None = None,
        sync_event: asyncio.Event | None = None,
    ):
        """Start measurement using given method parameters.

        Parameters
        ----------
        method: MethodParameters
            Method parameters for measurement
        callback: Callback, optional
            If specified, call this function on every new set of data points.
            New data points are batched, and contain all points since the last
            time it was called. Each point is a dictionary containing
            `frequency`, `z_re`, `z_im` for impedimetric techniques and
            `index`, `x`, `x_unit`, `x_type`, `y`, `y_unit` and `y_type` for
            non-impedimetric techniques.
        sync_event: asyncio.Event
            Event for hardware synchronization. Do not use directly.
            Instead, initiate hardware sync via `InstrumentPoolAsync.measure()`.
        """
        callback = callback or self.callback

        psmethod = method._to_psmethod()

        self.ensure_connection()

        self.validate_method(psmethod)

        measurement_manager = MeasurementManagerAsync(comm=self._comm)

        return await measurement_manager.measure(
            psmethod, callback=callback, sync_event=sync_event
        )

    def _initiate_hardware_sync_follower_channel(
        self,
        **kwargs,
    ) -> tuple[Coroutine[Any, Any, bool], asyncio.Future[Measurement]]:
        """Initiate hardware sync follower channel.

        Parameters
        ----------
        **kwargs
            There keyword arguments are passed to the measure function.

        Returns
        -------
        tuple[event, future]
            Activate the event to start the measurement.
            The second item is a future that contains the data once the measurement is finished.
        """
        self.ensure_connection()

        # Create event for hardware synchronization
        sync_event = asyncio.Event()
        measurement_future: asyncio.Future[Measurement] = asyncio.Future()

        async def start_measurement(
            *,
            manager: InstrumentManagerAsync,
            sync_event: asyncio.Event,
            measurement_future: asyncio.Future[Measurement],
            **kwargs,
        ):
            measurement = await manager.measure(
                sync_event=sync_event,
                **kwargs,
            )
            measurement_future.set_result(measurement)

        _ = asyncio.run_coroutine_threadsafe(
            start_measurement(
                manager=self,
                sync_event=sync_event,
                measurement_future=measurement_future,
                **kwargs,
            ),
            asyncio.get_running_loop(),
        )

        return sync_event.wait(), measurement_future

    async def wait_digital_trigger(self, wait_for_high: bool) -> None:
        """Wait for digital trigger.

        Parameters
        ----------
        wait_for_high: bool
            Wait for digital line high before starting
        """
        async with self._lock():
            while True:
                if await create_future(self._comm.DigitalLineD0Async()) == wait_for_high:
                    break
                await asyncio.sleep(0.05)

    async def abort(self) -> None:
        """Abort measurement."""
        async with self._lock():
            await create_future(self._comm.AbortAsync())

    async def initialize_multiplexer(self, mux_model: int) -> int:
        """Initialize the multiplexer.

        Parameters
        ----------
        mux_model: int
            The model of the multiplexer.
            - 0 = 8 channel
            - 1 = 16 channel
            - 2 = 32 channel

        Returns
        -------
        channels : int
            Number of available multiplexes channels
        """
        async with self._lock():
            model = MuxModel(mux_model)

            if model == MuxModel.MUX8R2 and (
                self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionPS4)
                )
                or self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionMS)
                )
            ):
                await create_future(self._comm.ClientConnection.ReadMuxInfoAsync())

            self._comm.Capabilities.MuxModel = model

            if self._comm.Capabilities.MuxModel == MuxModel.MUX8:
                self._comm.Capabilities.NumMuxChannels = 8
            elif self._comm.Capabilities.MuxModel == MuxModel.MUX16:
                self._comm.Capabilities.NumMuxChannels = 16
            elif self._comm.Capabilities.MuxModel == MuxModel.MUX8R2:
                await create_future(self._comm.ClientConnection.ReadMuxInfoAsync())

        channels = self._comm.Capabilities.NumMuxChannels
        return channels

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
        self.ensure_connection()

        if self._comm.Capabilities.MuxModel != MuxModel.MUX8R2:
            raise ValueError(
                f"Incompatible mux model: {self._comm.Capabilities.MuxModel}, expected 'MUXR2'."
            )

        mux_settings = PSMethod.MuxSettings(False)
        mux_settings.ConnSEWE = connect_sense_to_working_electrode
        mux_settings.ConnectCERE = combine_reference_and_counter_electrodes
        mux_settings.CommonCERE = use_channel_1_reference_and_counter_electrodes
        mux_settings.UnselWE = PSMethod.MuxSettings.UnselWESetting(
            set_unselected_channel_working_electrode
        )

        async with self._lock():
            await create_future(
                self._comm.ClientConnection.SetMuxSettingsAsync(MuxType(1), mux_settings)
            )

    async def set_multiplexer_channel(self, channel: int):
        """Sets the multiplexer channel.

        Parameters
        ----------
        channel : int
            Index of the channel to set.
        """
        async with self._lock():
            await create_future(self._comm.ClientConnection.SetMuxChannelAsync(channel))

    async def disconnect(self):
        """Disconnect from the instrument."""
        if not self.is_connected():
            return

        await create_future(self._comm.DisconnectAsync())
        del self._comm
