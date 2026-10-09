"""Submodule for instrument references and claims.

[InstrumentRef][] holds an instrument's metadata and status. Use
[InstrumentClaim][] as an async context manager for a claimed
instrument. The claim is released when the context exits.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self

from PalmSens.Sdk.Lablink.Example.Lablink.Mappers import MethodMappers

from .._converters import cr_string_to_sig_exp, pr_string_to_sig_exp
from .._types import AllowedCurrentRanges, AllowedPotentialRanges, MethodTypeCompatible
from ._measurement import MeasurementJob, MeasurementRef
from .models import InstrumentInfo
from .models._wire import ConfigureInstrumentsProperties, MeasuringRange, Volt

if TYPE_CHECKING:
    from ._session import Session


class InstrumentRef:
    """
    A reference to an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = (
        '_info',
        '_serial',
    )
    _serial: str
    _info: InstrumentInfo

    def __init__(self, serial: str):
        self._serial: str = serial

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial={self.serial_number!r})'

    def metadata(self) -> InstrumentInfo:
        return self._info

    @property
    def serial_number(self) -> str:
        """The serial number of the instrument."""
        return self._serial

    async def claim(self) -> InstrumentClaim: ...

    async def signalr_url(self) -> str: ...

    async def configuration(self) -> dict: ...

    async def capabilities(self) -> dict: ...

    async def current_measurement(self) -> MeasurementRef: ...

    async def state(self) -> dict: ...


class InstrumentClaim:
    """
    A context manager for claiming an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_serial', '_session')
    _serial: str
    _session: Session

    def __init__(self, serial: str, session: Session):
        self._serial = serial
        self._session = session

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial_number={self.serial_number!r})'

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
        await self._session.release(self)

    async def set_cell_mode(
        self, mode: Literal['unknown', 'potentiostatic', 'galvanostatic']
    ) -> None:
        """Sets the cell mode.

        Parameters
        ----------
        mode : str
            The desired cell mode.
        """
        payload = mode.capitalize()
        await self._session._http.post(f'/Instrument/{self._serial}/SetCellMode', json=payload)

    async def set_cell_state(self, state: Literal['unknown', 'off', 'on']) -> None:
        """Sets the cell state.

        Parameters
        ----------
        state : str
            The desired cell state.
        """
        payload = state.capitalize()
        await self._session._http.post(f'/Instrument/{self._serial}/SetCellState', json=payload)

    async def start_measurement(self, method: MethodTypeCompatible) -> MeasurementJob:
        """Starts a measurement."""
        dto = MethodMappers.ToDto(method._to_psmethod())

        payload = {
            'Technique': dto.Technique,
            'MethodParameters': dict(dto.Parameters),
        }

        response = await self._session._http.post(
            f'/Instrument/{self._serial}/StartMeasurement', json=payload
        )

        data = response.json()

        return MeasurementJob(guid=data['result'], serial=data['serial'])

    async def skip_pre_measurement_stage(self) -> None:
        """Skips the pre-measurement stage."""
        await self._session._http.post(f'/Instrument/{self._serial}/SkipPreMeasurementStage')

    async def pause_measurement(self) -> None:
        """Pauses the running measurement."""
        await self._session._http.post(f'/Instrument/{self._serial}/PauseMeasurement')

    async def resume_measurement(self) -> None:
        """Resumes a paused measurement."""
        await self._session._http.post(f'/Instrument/{self._serial}/ResumeMeasurement')

    async def abort_measurement(self) -> None:
        """Aborts the running measurement."""
        await self._session._http.post(f'/Instrument/{self._serial}/AbortMeasurement')

    async def set_custom_name(self, name: str) -> None:
        """Sets a custom display name for the instrument.

        Parameters
        ----------
        name : str
            The custom name to assign.
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
        """Applies a configuration payload to the instrument.

        Parameters
        ----------
        config : dict
            Configuration key-value pairs.
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
        payload = config.model_dump_json(exclude_none=True)

        await self._session._http.post(
            f'/Instrument/{self._serial}/ConfigureInstrument', json=payload
        )

    async def send_script(self, script: str) -> None:
        """Sends a script to the instrument.

        Parameters
        ----------
        script : str
            The script text to execute.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/SendScript', json=script)

    async def set_current_range(self, current_range: AllowedCurrentRanges) -> None:
        """Sets the current range.

        Parameters
        ----------
        current_range: AllowedCurrentRanges
            Set the current range as a string.
            See [pypalmsens.types.AllowedCurrentRanges][] for options.
        """
        # TODO: investigate intention behind MeasuringRange
        sig, exp = cr_string_to_sig_exp(current_range)
        config = MeasuringRange(Significant=sig, Exponent=exp)
        payload = config.model_dump_json()
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetCurrentRange',
            json=payload,
        )

    async def set_potential_range(self, potential_range: AllowedPotentialRanges) -> None:
        """Sets the potential range.

        Parameters
        ----------
        potential_range: AllowedPotentialRanges
            Set the potential range as a string.
            See [pypalmsens.types.AllowedPotentialRanges][] for options.
        """
        # TODO: investigate intention behind MeasuringRange
        sig, exp = pr_string_to_sig_exp(potential_range)
        config = MeasuringRange(Significant=sig, Exponent=exp)
        payload = config.model_dump_json()
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetPotentialRange', json=payload
        )

    async def set_current(self, current: float) -> None:
        """Sets the current value.

        Parameters
        ----------
        current : float
            The current to apply.
        """
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetCurrent',
            json=current,
        )

    async def set_potential(self, potential: float) -> None:
        """Sets the potential value.

        Parameters
        ----------
        potential : float
            The potential to apply.
        """
        await self._session._http.post(
            f'/Instrument/{self._serial}/SetPotential',
            json=potential,
        )

    async def set_bipot_state(self, state: bool) -> None:
        """Sets the bipot state.

        Parameters
        ----------
        state : bool
            The desired bipot state.
            True = on, False = off.
        """
        await self._session._http.post(f'/Instrument/{self._serial}/SetBiPotState', json=state)

    async def set_bipot_current_range(self, current_range: AllowedCurrentRanges) -> None:
        """Sets the bipot current range.

        Parameters
        ----------
        current_range: AllowedCurrentRanges
            Set the current range as a string.
            See [pypalmsens.types.AllowedPotentialRanges][] for options.
        """
        # TODO: investigate intention behind MeasuringRange
        sig, exp = cr_string_to_sig_exp(current_range)
        config = MeasuringRange(Significant=sig, Exponent=exp)
        payload = config.model_dump_json()

        await self._session._http.post(
            f'/Instrument/{self._serial}/SetBiPotCurrentRange',
            json=payload,
        )

    async def set_bipot_mode(self, mode: Literal['constant', 'offset']) -> None:
        """Sets the bipot mode.

        Parameters
        ----------
        mode : str
            The desired bipot mode.
        """
        payload = mode.capitalize()

        await self._session._http.post(f'/Instrument/{self._serial}/SetBiPotMode', json=payload)

    async def set_bipot_potential(self, potential: float) -> None:
        """Sets the bipot potential.

        Parameters
        ----------
        potential : float
            The potential to apply in bipot mode.
        """
        config = Volt(Value=potential)
        payload = config.model_dump_json()

        await self._session._http.post(
            f'/Instrument/{self._serial}/SetBiPotPotential',
            json=payload,
        )
