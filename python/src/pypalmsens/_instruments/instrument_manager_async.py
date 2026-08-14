from __future__ import annotations

import asyncio
import sys
import time
import warnings
from collections.abc import AsyncGenerator, Coroutine
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

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
    AllowedPotentialRanges,
    MethodTypeCompatible,
)
from ..data import Measurement
from .callback import Callback, CallbackEIS, CallbackStatus, Status
from .capabilities_mixin import CapabilitiesMixin
from .comm_protocol_async import CommProtocolAsync
from .events_mixin import EventsMixin
from .instrument import Instrument, discover_async
from .measurement_manager_async import MeasurementManagerAsync
from .shared import create_future, firmware_warning

WINDOWS = sys.platform == 'win32'
LINUX = not WINDOWS


warnings.simplefilter('default')


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

        [instrument] = available_instruments

    manager = InstrumentManagerAsync(instrument)
    await manager.connect()
    return manager


async def measure_async(
    method: MethodTypeCompatible,
    instrument: None | Instrument = None,
    callback: Callback | CallbackEIS | None = None,
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
        time it was called. Each point is an instance of `ps.data.CallbackData`
        for non-impedimetric or `ps.data.CallbackDataEIS`
        for impedimetric measurments.

    Returns
    -------
    measurement : Measurement
        Finished measurement.
    """
    async with await connect_async(instrument=instrument) as manager:
        measurement = await manager.measure(method, callback=callback)

    assert measurement

    return measurement


class InstrumentManagerAsync(CapabilitiesMixin, EventsMixin):
    """Asynchronous instrument manager for PalmSens instruments.

    Parameters
    ----------
    instrument: Instrument
        Instrument to connect to, use `discover()` to find connected instruments.
    """

    def __init__(self, instrument: Instrument):
        super().__init__()

        self.instrument: Instrument = instrument
        """Instrument being managed by this class."""

        self._comm: CommManager
        self._status_callback: CallbackStatus
        self._loop: asyncio.AbstractEventLoop

    @override
    def __repr__(self):
        return f"{type(self).__name__}('{self.instrument.id}', connected={self.is_connected()})"

    async def __aenter__(self):
        if not self.is_connected():
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    def is_measuring(self) -> bool:
        """Return True if device is measuring."""
        return int(self._comm.State) == CommManager.DeviceState.Measurement

    @asynccontextmanager
    async def _lock(self) -> AsyncGenerator[CommManager]:
        self.ensure_connection()

        await create_future(self._comm.ClientConnection.Semaphore.WaitAsync())

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

    async def connect(self) -> None:
        """Connect to instrument."""
        if self.is_connected():
            return

        self._comm = await self.instrument._connect_async()

        # Disable idle messages to improve response time and reduce noise
        await create_future(self._comm.SetStatusWhenIdleAsync(False))

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

    async def set_cell(self, cell_on: bool) -> None:
        """Turn the cell on or off.

        Parameters
        ----------
        cell_on : bool
            If true, turn on the cell
        """
        async with self._lock():
            await create_future(self._comm.SetCellOnAsync(cell_on))

    async def is_cell_on(self) -> bool:
        """Get cell status.

        Returns
        -------
        cell_on : bool
            Return true if the cell is on
        """
        async with self._lock():
            cell_on: bool = await create_future(self._comm.GetCellOnAsync())

        return cell_on

    async def read_current(self) -> float:
        """Read the current in µA.

        Returns
        -------
        current : float
            Current in µA.
        """
        async with self._lock():
            current: float = await create_future(self._comm.GetCurrentAsync())

        return single_to_double(current)

    async def get_current_range(self) -> AllowedCurrentRanges:
        """Get the current range for the cell.

        Returns
        -------
        current_range: AllowedCurrentRanges
        """
        async with self._lock():
            value: PalmSens.CurrentRange = await create_future(
                self._comm.GetCurrentRangeAsync()
            )

        return cr_enum_to_string(value)

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

    async def read_potential(self) -> float:
        """Read the potential in V.

        Returns
        -------
        potential : float
            Potential in V.
        """

        async with self._lock():
            potential: float = await create_future(self._comm.GetPotentialAsync())

        return single_to_double(potential)

    async def set_potential(self, potential: float) -> None:
        """Set the potential of the cell.

        Parameters
        ----------
        potential : float
            Potential in V
        """
        async with self._lock():
            await create_future(self._comm.SetPotentialAsync(potential))

    async def get_potential_range(self) -> AllowedPotentialRanges:
        """Get the potential range for the cell.

        Returns
        -------
        potential_range: AllowedPotentialRanges
        """
        async with self._lock():
            # no such api: self._comm.GetPotentialRangeAsync()
            return pr_enum_to_string(self._comm.PotentialRange)

    async def set_potential_range(self, potential_range: AllowedPotentialRanges):
        """Set the potential range for the cell.

        Parameters
        ----------
        potential_range: AllowedPotentialRanges
            Set the potential range as a string.
            See `pypalmsens.settings.AllowedPotentialRanges` for options.
        """
        async with self._lock():
            await create_future(
                self._comm.SetPotentialRangeAsync(pr_string_to_enum(potential_range))
            )

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

    async def measure(
        self,
        method: MethodTypeCompatible,
        *,
        callback: Callback | CallbackEIS | None = None,
        stream: Path | str | None = None,
        sync_event: asyncio.Event | None = None,
    ):
        """Start measurement using given method parameters.

        Parameters
        ----------
        method: MethodType
            Method parameters for measurement.
        callback: Callback, optional
            If specified, call this function on every new set of data points.
            New data points are batched, and contain all points since the last
            time it was called. Each point is an instance of `ps.data.CallbackData`
            for non-impedimetric or `ps.data.CallbackDataEIS`.
            for impedimetric measurments.
        stream: Path | str | None
            If defined, stream data directly to this file in JSON Lines text format
            (https://jsonlines.org). This option is useful for long-term measurements.
            In case of a PC crash or power outage, the most recent measurement data will
            still be available.
        sync_event: asyncio.Event
            Event for hardware synchronization. Do not use directly.
            Instead, initiate hardware sync via `InstrumentPoolAsync.measure()`.
        """
        self.ensure_connection()
        self.validate_method(method)  # type: ignore

        measurement_manager = MeasurementManagerAsync(comm=self._comm)

        return await measurement_manager.measure(
            method,
            callback=callback,
            stream=stream,
            sync_event=sync_event,
            listeners=self._listeners,
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

    async def query(self, command: str, delay: float | None = None) -> str:
        """Send a command using the communication protocol and return its response.

        This is a method for direct communication with the instrument.
        It writes the command to the device, waits for completion,
        reads the full response, and returns it as a string.

        For commands that run for a long time (e.g. scripts), this
        method will block until the script completes or times out.

        See also [pypalmsens.CommProtocolAsync][].

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

        emit_idle_messages: bool

        async with self._lock():
            # this temporarily turns off idle messages to reduce cross-talk
            if emit_idle_messages := await create_future(self._comm.GetStatusWhenIdleAsync()):
                await create_future(self._comm.SetStatusWhenIdleAsync(False))

            comm = CommProtocolAsync(self.instrument)

            try:
                response = await comm.query(command, delay=delay)
            finally:
                if emit_idle_messages:
                    await create_future(self._comm.SetStatusWhenIdleAsync(emit_idle_messages))

        return response

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
            model = PalmSens.MuxModel(mux_model)

            if model == PalmSens.MuxModel.MUX8R2 and (
                self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionPS4)
                )
                or self._comm.ClientConnection.GetType().Equals(
                    clr.GetClrType(PalmSens.Comm.ClientConnectionMS)
                )
            ):
                await create_future(self._comm.ClientConnection.ReadMuxInfoAsync())

            self._comm.Capabilities.MuxModel = model

            if self._comm.Capabilities.MuxModel == PalmSens.MuxModel.MUX8:
                self._comm.Capabilities.NumMuxChannels = 8
            elif self._comm.Capabilities.MuxModel == PalmSens.MuxModel.MUX16:
                self._comm.Capabilities.NumMuxChannels = 16
            elif self._comm.Capabilities.MuxModel == PalmSens.MuxModel.MUX8R2:
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

        if self._comm.Capabilities.MuxModel != PalmSens.MuxModel.MUX8R2:
            raise ValueError(
                f"Incompatible mux model: {self._comm.Capabilities.MuxModel}, expected 'MUXR2'."
            )

        mux_settings = PalmSens.Method.MuxSettings(False)
        mux_settings.ConnSEWE = connect_sense_to_working_electrode
        mux_settings.ConnectCERE = combine_reference_and_counter_electrodes
        mux_settings.CommonCERE = use_channel_1_reference_and_counter_electrodes
        mux_settings.UnselWE = PalmSens.Method.MuxSettings.UnselWESetting(
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

        # https://github.com/PalmSens/palmsens-sdk/pull/447#issuecomment-5291235608
        await asyncio.sleep(0.5)

        await create_future(self._comm.DisconnectAsync())
        self._comm.Dispose()
        del self._comm
