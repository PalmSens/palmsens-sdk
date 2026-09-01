from __future__ import annotations

import asyncio
import time
import warnings
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

import clr
import PalmSens
from PalmSens.Comm import CommManager, MuxType
from typing_extensions import override

from .._converters import (
    cr_enum_to_string,
    cr_string_to_enum,
    pr_enum_to_string,
    pr_string_to_enum,
    single_to_double,
)
from .._types import (
    AllowedCurrentRanges,
    AllowedMuxModels,
    AllowedPotentialRanges,
    MethodTypeCompatible,
)
from ..data import Measurement
from .callback import Callback, CallbackEIS, Status
from .capabilities_mixin import CapabilitiesMixin
from .comm_protocol import CommProtocol
from .events_mixin import EventsMixin
from .gpio import Gpio
from .instrument import Instrument, discover
from .measurement_manager_async import MeasurementManagerAsync
from .shared import firmware_warning

warnings.simplefilter('default')


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

        [instrument] = available_instruments

    manager = InstrumentManager(instrument)
    manager.connect()
    return manager


def measure(
    method: MethodTypeCompatible,
    instrument: None | Instrument = None,
    callback: Callback | CallbackEIS | None = None,
    stream: str | Path | None = None,
) -> Measurement:
    """Run measurement.

    Executes the given method on any plugged-in PalmSens USB device.
    Error if multiple devices are plugged-in.

    Parameters
    ----------
    instrument : Instrument, optional
        Connect to and meassure on a specific instrument.
        Use `pypalmsens.discover()` to discover instruments.
    callback: Callback | CallbackEIS, optional
        If specified, call this function on every new set of data points.
        New data points are batched, and contain all points since the last
        time it was called. Each point is an instance of `ps.data.CallbackData`
        for non-impedimetric or `ps.data.CallbackDataEIS`
        for impedimetric measurments.
    stream: Path | str | None
        If defined, stream data directly to this file in JSON Lines text format
        (https://jsonlines.org). This option is useful for long-term measurements.
        In case of a PC crash or power outage, the most recent measurement data will
        still be available.

    Returns
    -------
    measurement : Measurement
        Finished measurement.
    """
    with connect(instrument=instrument) as manager:
        measurement = manager.measure(method, callback=callback, stream=stream)

    assert measurement

    return measurement


class InstrumentManager(CapabilitiesMixin, EventsMixin):
    """Instrument manager for PalmSens instruments.

    Parameters
    ----------
    instrument: Instrument
        Instrument to connect to, use `discover()` to find connected instruments.
    """

    def __init__(self, instrument: Instrument):
        super().__init__()

        self.instrument: Instrument = instrument
        """Instrument being managed by this class."""

        self.gpio: Gpio = Gpio(self)
        """High-level GPIO interface."""

        self._comm: CommManager

    @override
    def __repr__(self):
        return f"{type(self).__name__}('{self.instrument.id}', connected={self.is_connected()})"

    def __enter__(self):
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, *_):
        self.disconnect()

    def is_measuring(self) -> bool:
        """Return True if device is measuring."""
        return int(self._comm.State) == CommManager.DeviceState.Measurement

    @contextmanager
    def _lock(self) -> Generator[CommManager]:
        self.ensure_connection()

        self._comm.ClientConnection.Semaphore.Wait()

        try:
            yield self._comm

        finally:
            if self._comm.ClientConnection.Semaphore.CurrentCount == 0:
                _ = self._comm.ClientConnection.Semaphore.Release()

    def is_connected(self) -> bool:
        """Return True if an instrument connection exists."""
        return hasattr(self, '_comm')

    def ensure_connection(self):
        """Raises connection error if the instrument is not connected."""
        if not self.is_connected():
            raise ConnectionError('Not connected to an instrument')

    def connect(self) -> None:
        """Connect to instrument."""
        if self.is_connected():
            return

        # The comm manager needs to open async, because the measurement is handled async.
        # Opening the comm manager in async sets some handlers in ClientConnection
        # that are sync or async specific. This affects the measurement,
        # receive status, and device state change events.
        self._comm = asyncio.run(self.instrument._connect_async())

        # Disable idle messages to improve response time and reduce noise
        self._comm.StatusWhenIdle = False

        firmware_warning(self._comm.Capabilities)

    def status(self) -> Status:
        """Get status.

        Sets device 'StatusWhenIdle' flag on device, which tells it
        to periodically send an updated status message.
        """
        self.ensure_connection()

        if not self._comm.StatusWhenIdle:
            self._comm.StatusWhenIdle = True

            while not (status := self._comm.get_Status()):
                time.sleep(0.1)

        else:
            status = self._comm.get_Status()

        return Status(
            status,
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

    def is_cell_on(self) -> bool:
        """Get cell status.

        Returns
        -------
        cell_on : bool
            Return true if the cell is on
        """
        with self._lock():
            return self._comm.CellOn

    def read_current(self) -> float:
        """Read the current in µA.

        Returns
        -------
        current : float
            Current in µA.
        """
        with self._lock():
            current = self._comm.Current

        return single_to_double(current)

    def get_current_range(self) -> AllowedCurrentRanges:
        """Get the current range for the cell.

        Returns
        -------
        current_range: AllowedCurrentRanges
        """
        with self._lock():
            return cr_enum_to_string(self._comm.CurrentRange)

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

    def read_potential(self) -> float:
        """Read the potential in V.

        Returns
        -------
        potential : float
            Potential in V.
        """

        with self._lock():
            potential = self._comm.Potential

        return single_to_double(potential)

    def set_potential(self, potential: float):
        """Set the potential of the cell.

        Parameters
        ----------
        potential : float
            Potential in V
        """
        with self._lock():
            self._comm.Potential = potential

    def get_potential_range(self) -> AllowedPotentialRanges:
        """Get the potential range for the cell.

        Returns
        -------
        potential_range: AllowedPotentialRanges
        """
        with self._lock():
            return pr_enum_to_string(self._comm.PotentialRange)

    def set_potential_range(self, potential_range: AllowedPotentialRanges):
        """Set the potential range for the cell.

        Parameters
        ----------
        potential_range: AllowedPotentialRanges
            Set the potential range as a string.
            See `pypalmsens.settings.AllowedPotentialRanges` for options.
        """
        with self._lock():
            self._comm.PotentialRange = pr_string_to_enum(potential_range)

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

    def measure(
        self,
        method: MethodTypeCompatible,
        *,
        callback: Callback | CallbackEIS | None = None,
        stream: Path | str | None = None,
    ) -> Measurement:
        """Start measurement using given method parameters.

        Parameters
        ----------
        method: MethodType
            Method parameters for measurement
        callback: Callback, optional
            If specified, call this function on every new set of data points.
            New data points are batched, and contain all points since the last
            time it was called. Each point is an instance of `ps.data.CallbackData`
            for non-impedimetric or  `ps.data.CallbackDataEIS`
            for impedimetric measurments.
        stream: Path | str | None
            If defined, stream data directly to this file in JSON Lines text format
            (https://jsonlines.org). This option is useful for long-term measurements.
            In case of a PC crash or power outage, the most recent measurement data will
            still be available.

        Returns
        -------
        measurement : Measurement
            Finished measurement.
        """
        self.ensure_connection()
        self.validate_method(method)

        # note that the comm manager must be opened async so it sets the
        # correct async event handlers
        measurement_manager = MeasurementManagerAsync(comm=self._comm)

        return asyncio.run(
            measurement_manager.measure(
                method,
                callback=callback,
                stream=stream,
                listeners=self._listeners,
            )
        )

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
                time.sleep(0.05)

    def abort(self) -> None:
        """Abort measurement."""
        with self._lock():
            self._comm.Abort()

    def query(self, command: str, delay: float | None = None) -> str:
        """Send a command using the communication protocol and return its response.

        This is a method for direct communication with the instrument.
        It writes the command to the device, waits for completion,
        reads the full response, and returns it as a string.

        For commands that run for a long time (e.g. scripts), this
        method will block until the script completes or times out.

        See also [pypalmsens.CommProtocol][].

        Parameters
        ----------
        command : str
            The command to send (e.g., 'i' to get the serial number).
            If `command` does not end with `'\\n'`, one is automatically added.
        delay : float, optional
            Pause (in seconds) between read attempts. Defaults to `self.delay`.

        Returns
        -------
        response : str
            The complete response from the device.
        """
        if not isinstance(self._comm.ClientConnection, PalmSens.Comm.ClientConnectionMS):
            raise TypeError(
                'The Communication Protocol is only supported on MethodSCRIPT devices.'
            )

        with self._lock():
            # this temporarily turns off idle messages to reduce cross-talk
            if emit_idle_messages := self._comm.get_StatusWhenIdle():
                self._comm.set_StatusWhenIdle(False)

            comm = CommProtocol(self.instrument)

            try:
                response = comm.query(command, delay=delay)
            finally:
                if emit_idle_messages:
                    self._comm.set_StatusWhenIdle(True)

        return response

    def initialize_multiplexer(self, model: AllowedMuxModels) -> int:
        """Initialize the multiplexer.

        Parameters
        ----------
        model : Literal['mux8', 'mux16', 'mux8r2']
            The model of the multiplexer.

            - 'mux8': 8 channels
            - 'mux16': 16 channels
            - 'mux8r2': 8 to 128 channels

        Returns
        -------
        channels : int
            Number of available multiplexes channels
        """
        mux_model = {
            'mux8': PalmSens.MuxModel.MUX8,
            'mux16': PalmSens.MuxModel.MUX16,
            'mux8r2': PalmSens.MuxModel.MUX8R2,
        }[model]

        with self._lock():
            if mux_model == PalmSens.MuxModel.MUX8R2 and (
                self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionPS4)
                )
                or self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionMS)
                )
            ):
                self._comm.ClientConnection.ReadMuxInfo()

            self._comm.Capabilities.MuxModel = mux_model

            if self._comm.Capabilities.MuxModel == PalmSens.MuxModel.MUX8:
                self._comm.Capabilities.NumMuxChannels = 8
            elif self._comm.Capabilities.MuxModel == PalmSens.MuxModel.MUX16:
                self._comm.Capabilities.NumMuxChannels = 16
            elif self._comm.Capabilities.MuxModel == PalmSens.MuxModel.MUX8R2:
                self._comm.ClientConnection.ReadMuxInfo()

        channels = self._comm.Capabilities.NumMuxChannels
        return channels

    def configure_mux8r2(
        self,
        *,
        connect_se_we: bool = False,
        combine_re_ce: bool = False,
        common_re_ce: bool = False,
        unused_we: Literal['float', 'ground', 'standby'] = 'float',
    ):
        """Configure the Mux8R2 multiplexer.

        This method sets the Mux8R2 parameters globally, including for techniques.
        If you specify [pypalmsens.settings.Multiplexer][] in your technique,
        those settings will override the values set here.

        Parameters
        ---------
        connect_se_we : bool, optional
            Connect the sense electrode to the working electrode. Default is False.
        combine_re_ce : bool, optional
            Combine the reference and counter electrodes. Default is False.
        common_re_ce : bool, optional
            Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
        unused_we : Literal['float', 'ground', 'standby'], optional
            State of the unused channel working electrodes: floating,
            ground, or standby potential. Default is 'float'.
        """
        self.ensure_connection()

        if self._comm.Capabilities.MuxModel != PalmSens.MuxModel.MUX8R2:
            raise ValueError(
                f"Incompatible mux model: {self._comm.Capabilities.MuxModel}, expected 'MUXR2'."
            )

        mux_settings = PalmSens.Method.MuxSettings(False)
        mux_settings.ConnSEWE = connect_se_we
        mux_settings.ConnectCERE = combine_re_ce
        mux_settings.CommonCERE = common_re_ce
        unused_we_setting = {
            'float': PalmSens.Method.MuxSettings.UnselWESetting.FLOAT,
            'ground': PalmSens.Method.MuxSettings.UnselWESetting.GND,
            'standby': PalmSens.Method.MuxSettings.UnselWESetting.VSTDBY,
        }[unused_we]
        mux_settings.UnselWE = unused_we_setting

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
        self._comm.Dispose()

        del self._comm
