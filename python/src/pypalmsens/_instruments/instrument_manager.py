from __future__ import annotations

import asyncio
import warnings
from contextlib import contextmanager
from time import sleep
from typing import Iterator

import clr
import PalmSens
import System
from PalmSens import Method as PSMethod
from PalmSens import MuxModel
from PalmSens.Comm import CommManager, MuxType
from typing_extensions import override

from .._methods import (
    AllowedCurrentRanges,
    BaseTechnique,
    cr_string_to_enum,
)
from ..data import Measurement
from .callback import Callback, Status
from .instrument_manager_async import discover_async
from .measurement_manager_async import MeasurementManagerAsync
from .shared import Instrument, create_future, firmware_warning

warnings.simplefilter('default')


def discover(
    ftdi: bool = True,
    usbcdc: bool = True,
    winusb: bool = True,
    bluetooth: bool = False,
    serial: bool = True,
    ignore_errors: bool = False,
) -> list[Instrument]:
    """Discover instruments.

    For a list of device interfaces, see:
        https://sdk.palmsens.com/python/latest//installation.html#compatibility

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
    return asyncio.run(
        discover_async(
            ftdi=ftdi,
            usbcdc=usbcdc,
            winusb=winusb,
            bluetooth=bluetooth,
            serial=serial,
            ignore_errors=ignore_errors,
        )
    )


def connect(
    instrument: None | Instrument = None,
) -> InstrumentManager:
    """Connect to instrument and return InstrumentManager.

    Connects to any plugged-in PalmSens USB device.
    Error if multiple devices are plugged-in.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to a specific instrument.
        Use `pypalmsens.discover()` to discover instruments.

    Returns
    -------
    manager : InstrumentManager
        Return instance of `InstrumentManager` connected to the given instrument.
    """
    if not instrument:
        available_instruments = discover(ignore_errors=True)

        if not available_instruments:
            raise ConnectionError('No instruments were discovered.')

        if len(available_instruments) > 1:
            raise ConnectionError('More than one device discovered.')

        instrument = available_instruments[0]

    manager = InstrumentManager(instrument)
    manager.connect()
    return manager


def measure(
    method: BaseTechnique,
    instrument: None | Instrument = None,
    callback: Callback | None = None,
) -> Measurement:
    """Run measurement.

    Executes the given method on any plugged-in PalmSens USB device.
    Error if multiple devices are plugged-in.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to and meassure on a specific instrument.
        Use `pypalmsens.discover()` to discover instruments.
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
    with connect(instrument=instrument) as manager:
        measurement = manager.measure(method, callback=callback)

    assert measurement

    return measurement


class InstrumentManager:
    """Instrument manager for PalmSens instruments.

    Parameters
    ----------
    instrument: Instrument
        Instrument to connect to, use `discover()` to find connected instruments.
    """

    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        """Instrument to connect to."""

        self._comm: CommManager

    @override
    def __repr__(self):
        return (
            f'{self.__class__.__name__}({self.instrument.id}, connected={self.is_connected()})'
        )

    def __enter__(self):
        if not self.is_connected():
            _ = self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _ = self.disconnect()

    def is_measuring(self) -> bool:
        """Return True if device is measuring."""
        return int(self._comm.State) == CommManager.DeviceState.Measurement

    @contextmanager
    def _lock(self) -> Iterator[CommManager]:
        self.ensure_connection()

        self._comm.ClientConnection.Semaphore.Wait()

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

    def connect(self) -> None:
        """Connect to instrument."""
        if self.is_connected():
            return

        async def _connect(psinstrument: PalmSens.Devices.Device) -> CommManager:
            try:
                await create_future(psinstrument.OpenAsync())
            except System.UnauthorizedAccessException as err:
                raise ConnectionError(
                    f'Cannot open instrument connection (reason: {err.Message}). Check if the device is already in use.'
                ) from err

            return await create_future(CommManager.CommManagerAsync(psinstrument))

        # The comm manager needs to open async, because the measurement is handled async.
        # Opening the comm manager in async sets some handlers in ClientConnection
        # that are sync or async specific. This affects the measurement,
        # receive status, and device state change events.
        self._comm = asyncio.run(_connect(self.instrument.device))

        firmware_warning(self._comm.Capabilities)

    def status(self) -> Status:
        """Get status."""
        return Status(
            self._comm.get_Status(),
            device_state=str(self._comm.get_State()),  # type:ignore
        )

    def set_cell(self, cell_on: bool):
        """Turn the cell on or off.

        Parameters
        ----------
        cell_on : bool
            If true, turn on the cell
        """
        with self._lock():
            self._comm.CellOn = cell_on

    def set_potential(self, potential: float):
        """Set the potential of the cell.

        Parameters
        ----------
        potential : float
            Potential in V
        """
        with self._lock():
            self._comm.Potential = potential

    def set_current_range(self, current_range: AllowedCurrentRanges):
        """Set the current range for the cell.

        Parameters
        ----------
        current_range: AllowedCurrentRanges
            Set the current range as a string.
            See `pypalmsens.settings.AllowedCurrentRanges` for options.
        """
        with self._lock():
            self._comm.CurrentRange = cr_string_to_enum(current_range)

    def read_current(self) -> float:
        """Read the current in µA.

        Returns
        -------
        current : float
            Current in µA.
        """
        with self._lock():
            current = self._comm.Current

        return current

    def read_potential(self) -> float:
        """Read the potential in V.

        Returns
        -------
        potential : float
            Potential in V.
        """

        with self._lock():
            potential = self._comm.Potential

        return potential

    def get_instrument_serial(self) -> str:
        """Return instrument serial number.

        Returns
        -------
        serial : str
            Instrument serial.
        """
        with self._lock():
            serial = self._comm.DeviceSerial.ToString()

        return serial

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

    def measure(
        self,
        method: BaseTechnique,
        *,
        callback: Callback | None = None,
    ) -> Measurement:
        """Start measurement using given method parameters.

        Parameters
        ----------
        method: Method parameters
            Method parameters for measurement
        callback: Callback, optional
            If specified, call this function on every new set of data points.
            New data points are batched, and contain all points since the last
            time it was called. Each point is an instance of `ps.data.CallbackData`
            for non-impedimetric or  `ps.data.CallbackDataEIS`
            for impedimetric measurments.

        Returns
        -------
        measurement : Measurement
            Finished measurement.
        """
        psmethod = method._to_psmethod()

        self.ensure_connection()

        self.validate_method(psmethod)

        # note that the comm manager must be opened async so it sets the
        # correct async event handlers
        measurement_manager = MeasurementManagerAsync(comm=self._comm)

        return asyncio.run(measurement_manager.measure(psmethod, callback=callback))

    def wait_digital_trigger(self, wait_for_high: bool):
        """Wait for digital trigger.

        Parameters
        ----------
        wait_for_high: bool
            Wait for digital line high before starting
        """
        with self._lock():
            while True:
                if self._comm.DigitalLineD0 == wait_for_high:
                    break
                sleep(0.05)

    def abort(self) -> None:
        """Abort measurement."""
        with self._lock():
            self._comm.Abort()

    def initialize_multiplexer(self, mux_model: int) -> int:
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
        with self._lock():
            model = MuxModel(mux_model)

            if model == MuxModel.MUX8R2 and (
                self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionPS4)
                )
                or self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionMS)
                )
            ):
                self._comm.ClientConnection.ReadMuxInfo()

            self._comm.Capabilities.MuxModel = model

            if self._comm.Capabilities.MuxModel == MuxModel.MUX8:
                self._comm.Capabilities.NumMuxChannels = 8
            elif self._comm.Capabilities.MuxModel == MuxModel.MUX16:
                self._comm.Capabilities.NumMuxChannels = 16
            elif self._comm.Capabilities.MuxModel == MuxModel.MUX8R2:
                self._comm.ClientConnection.ReadMuxInfo()

        channels = self._comm.Capabilities.NumMuxChannels
        return channels

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

        with self._lock():
            self._comm.ClientConnection.SetMuxSettings(MuxType(1), mux_settings)

    def set_multiplexer_channel(self, channel: int):
        """Sets the multiplexer channel.

        Parameters
        ----------
        channel : int
            Index of the channel to set.
        """
        with self._lock():
            self._comm.ClientConnection.SetMuxChannel(channel)

    def disconnect(self):
        """Disconnect from the instrument."""
        if not self.is_connected():
            return

        self._comm.Disconnect()

        del self._comm
