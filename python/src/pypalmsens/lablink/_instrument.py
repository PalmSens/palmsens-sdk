"""Submodule for instrument references and claims.

[Instrument][] holds an instrument's metadata and status. Use
[InstrumentClaim][] as an async context manager for a claimed
instrument. The claim is released when the context exits.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Literal, Protocol, Self, runtime_checkable

from PalmSens.Sdk.Lablink.Example.Lablink.Mappers import MethodMappers

from .._converters import cr_string_to_sig_exp, pr_string_to_sig_exp
from .._types import AllowedCurrentRanges, AllowedPotentialRanges, MethodTypeCompatible
from ._measurement import Measurement, MeasurementJob
from .models._wire import (
    CellMode,
    CellState,
    ConfigureInstrumentsProperties,
    MeasuringRange,
    Volt,
)

if TYPE_CHECKING:
    from ._session import Session


@runtime_checkable
class Releasable(Protocol):
    async def release(self) -> None: ...

    @property
    def serial_number(self) -> str: ...


class InstrumentReadsMixin:
    _serial: str
    _session: Session

    @property
    def info(self) -> dict[str, Any]:
        """The instrument info from the most recent [get_info][] call.

        May be stale or empty.
        """
        return self._session.instrument_info[self._serial]

    async def get_info(self) -> dict[str, Any]:
        """Get info for instrument.

        Returns a dictionary of the most recent instrument info.
        The data may be stale or empty if no measurement has been run.
        """
        info = await self._session.get_instrument_info()
        return info[self._serial]

    async def get_signalr_url(self) -> str:
        """Return the signal rate URL for this instrument."""
        response = await self._session._http.get(f'/Instrument/{self._serial}/GetSignalRUrl')
        data = response.json()
        return data['result']

    async def get_configuration(self) -> dict[str, Any]:
        """Fetch the current configuration for this instrument.

        Returns a dictionary of configured settings.
        """
        response = await self._session._http.get(f'/Instrument/{self._serial}/Configuration')
        data = response.json()
        return data['result']

    async def get_capabilities(self) -> dict[str, Any]:
        """Fetch the capabilities of this instrument.

        Returns a dictionary of supported features.
        """
        response = await self._session._http.get(f'/Instrument/{self._serial}/Capabilities')
        data = response.json()
        return data['result']

    async def get_active_measurement(self) -> Measurement:
        """Return the active measurement, if any."""
        response = await self._session._http.get(
            f'/Instrument/{self._serial}/CurrentMeasurement'
        )
        data = response.json()
        guid = data['result']['id']
        return Measurement(guid=guid, session=self._session)

    async def get_state(self) -> dict[str, Any]:
        """Fetch the current state of this instrument.

        Returns a dictionary describing the device state.
        """
        response = await self._session._http.get(f'/Instrument/{self._serial}/State')
        data = response.json()
        return data['result']


class Instrument(InstrumentReadsMixin):
    """
    A reference to an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_serial', '_session')

    def __init__(self, serial: str, session: Session):
        self._serial: str = serial
        self._session: Session = session

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial={self.serial_number!r})'

    def __eq__(self, other: object) -> bool:  # value semantics: serial only
        return isinstance(other, Instrument) and self._serial == other._serial

    def __hash__(self) -> int:
        return hash(self._serial)

    @property
    def serial_number(self) -> str:
        """The serial number of the instrument."""
        return self._serial

    async def claim(self, *, auto_release: bool = False) -> InstrumentClaim:
        """Claim this instrument.

        The claim is held until you release it, or until the enclosing
        `async with` block exits.

        Parameters
        ----------
        auto_release: bool, optional
            If True, the server releases the claim after measurement ends.
        """
        method = 'Claim' if auto_release else 'ManualClaim'
        await self._session._http.post(f'/Instrument/{self._serial}/{method}')
        return InstrumentClaim(self._serial, self._session)


class InstrumentClaim(InstrumentReadsMixin):
    """
    A context manager for claiming an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_serial', '_session')

    def __init__(self, serial: str, session: Session):
        self._serial: str = serial
        self._session: Session = session

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial_number={self.serial_number!r})'

    def __eq__(self, other: object) -> bool:  # value semantics: serial only
        return isinstance(other, InstrumentClaim) and self._serial == other._serial

    def __hash__(self) -> int:
        return hash(self._serial)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc) -> None:
        await self.release()

    @property
    def serial_number(self) -> str:
        """The serial number of the claimed instrument."""
        return self._serial

    async def release(self) -> None:
        """Release the instrument claim."""
        await self._session._http.post(f'/Instrument/{self._serial}/Unclaim')

    async def set_cell_mode(
        self, mode: Literal['unknown', 'potentiostatic', 'galvanostatic']
    ) -> None:
        """Sets the cell mode.

        Parameters
        ----------
        mode : str
            The desired cell mode.
        """
        payload = CellMode[mode.capitalize()].value
        await self._session._http.post(f'/Instrument/{self._serial}/SetCellMode', json=payload)

    async def set_cell_state(self, state: Literal['unknown', 'off', 'on']) -> None:
        """Sets the cell state.

        Parameters
        ----------
        state : str
            The desired cell state.
        """
        payload = CellState[state.capitalize()].value
        await self._session._http.post(f'/Instrument/{self._serial}/SetCellState', json=payload)

    async def start_measurement(self, method: MethodTypeCompatible) -> MeasurementJob:
        """Start a measurement.

        Parameters
        ----------
        method : MethodTypeCompatible
            The measurement technique and parameters to run.
        """
        dto = MethodMappers.ToDto(method._to_psmethod())

        payload = {
            'Technique': dto.Technique,
            'MethodParameters': dict(dto.Parameters),
        }

        response = await self._session._http.post(
            f'/Instrument/{self._serial}/StartMeasurement', json=payload
        )

        data = response.json()

        return MeasurementJob(guid=data['result'], claim=self)

    async def skip_pre_measurement_stage(self) -> None:
        """Skip the initial pre-measurement setup step.

        Useful when you want to begin measuring without running
        through all calibration steps.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/SkipPreMeasurementStage')

    async def pause_measurement(self) -> None:
        """Pause a running measurement.

        The instrument holds its current state and resumes later.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/PauseMeasurement')

    async def resume_measurement(self) -> None:
        """Resume a previously paused measurement."""
        await self._session._http.post(f'/Instrument/{self._serial}/ResumeMeasurement')

    async def abort_measurement(self) -> None:
        """Stop and release a running measurement.

        The instrument resets to the pre-measurement state after aborting.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/AbortMeasurement')

    async def set_custom_name(self, name: str) -> None:
        """Set a custom display name for the instrument.

        Parameters
        ----------
        name : str
            The name to show on the device screen.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/SetCustomName', json=name)

    async def configure(
        self,
        mains_frequency: Literal['Undefined', 'Hz50', 'Hz60', 'DontCare'] | None = None,
        signal_train: Literal['Undefined', 'LowSpeed', 'HighSpeed', 'MaximumRange']
        | None = None,
        hardware_sync_allowed: bool | None = None,
        multichannel_role: Literal['Undefined', 'Standalone', 'Master', 'Slave'] | None = None,
    ) -> None:
        """Apply configuration settings to this instrument.

        Parameters
        ----------
        mains_frequency : str or None, optional
            Mains frequency in Hz (e.g. '50' or '60'). Use 'Undefined' for auto.
        signal_train : str or None, optional
            Speed of the analog input train (e.g. 'LowSpeed', 'HighSpeed').
        hardware_sync_allowed : bool or None, optional
            Whether to use hardware synchronization.
        multichannel_role : str or None, optional
            Role for multi-channel mode ('Standalone', 'Master', 'Slave').
        """
        config = ConfigureInstrumentsProperties.model_validate(
            {
                'MainsFrequency': mains_frequency,
                'SignalTrain': signal_train,
                'HardwareSyncAllowed': hardware_sync_allowed,
                'MultiChannelRole': multichannel_role,
            }
        )
        # TODO: How does the endpoint handle null?
        # If the endpoint treats this as a patch,
        # nulls may clear settings or be rejected
        payload = config.model_dump(exclude_none=True)

        await self._session._http.post(
            f'/Instrument/{self._serial}/ConfigureInstrument', json=payload
        )

    async def start_workflow(self, workflow: str) -> None:
        """Start a workflow on the instrument.

        Parameters
        ----------
        workflow : str
            Name of the workfrow to execute on the instrument.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/SendScript', json=workflow)

    async def set_current_range(self, current_range: AllowedCurrentRanges) -> None:
        """Set the current measurement range.

        Parameters
        ----------
        current_range : AllowedCurrentRanges
            The desired range as a string (e.g. '1 mA'). See [pypalmsens.types.AllowedCurrentRanges][] for options.
        """
        # TODO: investigate intention behind MeasuringRange
        sig, exp = cr_string_to_sig_exp(current_range)
        config = MeasuringRange(Significant=sig, Exponent=exp)
        payload = config.model_dump()
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetCurrentRange',
            json=payload,
        )

    async def set_potential_range(self, potential_range: AllowedPotentialRanges) -> None:
        """Set the potential measurement range.

        Parameters
        ----------
        potential_range : AllowedPotentialRanges
            The desired range as a string (e.g. '100 mV'). See [pypalmsens.types.AllowedPotentialRanges][] for options.
        """
        # TODO: investigate intention behind MeasuringRange
        sig, exp = pr_string_to_sig_exp(potential_range)
        config = MeasuringRange(Significant=sig, Exponent=exp)
        payload = config.model_dump()
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetPotentialRange', json=payload
        )

    async def set_current(self, current: float) -> None:
        """Set the cell current (galvanostatic mode).

        Parameters
        ----------
        current : float
            Current value in µA.
        """
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetCurrent',
            json=current,
        )

    async def set_potential(self, potential: float) -> None:
        """Set the working electrode (WE) potential relative to the reference
        electrode (RE).

        Parameters
        ----------
        potential : float
            WE potential in volts.
        """
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetPotential',
            json=potential,
        )

    async def set_bipot_enabled(self, state: bool) -> None:
        """Enable or disable the bipotentiostat (the second working electrode).

        Parameters
        ----------
        state : bool
            True = bipotentiostat on (WE2 active), False = off.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/SetBiPotState', json=state)

    async def set_bipot_current_range(self, current_range: AllowedCurrentRanges) -> None:
        """Set the current range of the second working electrode (WE2).

        Parameters
        ----------
        current_range : AllowedCurrentRanges
            Desired WE2 current range as a string (e.g. '1 mA').
        """
        # TODO: investigate intention behind MeasuringRange
        sig, exp = cr_string_to_sig_exp(current_range)
        config = MeasuringRange(Significant=sig, Exponent=exp)
        payload = config.model_dump()

        await self._session._http.post(
            f'/Instrument/{self._serial}/SetBiPotCurrentRange',
            json=payload,
        )

    async def set_bipot_mode(self, mode: Literal['constant', 'offset']) -> None:
        """Set how the second working electrode (WE2) is coupled to WE1.

        - `constant`: WE2 is held at a fixed potential vs. the RE while
          WE1 is stepped or swept independently.
        - `offset`: WE2 tracks WE1, maintained at a fixed potential
          difference from WE1 as WE1 changes.

        Parameters
        ----------
        mode : str
            Coupling mode: 'constant' or 'offset'.
        """
        payload = CellMode[mode.capitalize()].value

        await self._session._http.post(f'/Instrument/{self._serial}/SetBiPotMode', json=payload)

    async def set_bipot_potential(self, potential: float) -> None:
        """Set the potential of the second working electrode (WE2).

        Parameters
        ----------
        potential : float
            WE2 setpoint in volts. Absolute vs. RE in constant mode, or the
            WE1-relative offset in offset mode.
        """
        config = Volt(Value=potential)
        payload = config.model_dump()

        await self._session._http.post(
            f'/Instrument/{self._serial}/SetBiPotPotential',
            json=payload,
        )
