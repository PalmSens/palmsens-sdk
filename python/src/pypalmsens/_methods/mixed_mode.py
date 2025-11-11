from __future__ import annotations

from typing import ClassVar, Literal, Protocol, runtime_checkable

import attrs
from PalmSens import Method as PSMethod
from PalmSens.Techniques import MixedMode as PSMixedMode
from typing_extensions import override

from .._shared import single_to_double
from . import mixins
from ._shared import (
    CURRENT_RANGE,
)
from .base import BaseTechnique


@runtime_checkable
class BaseStage(Protocol):
    """Protocol to provide base methods for stage classes."""

    __attrs_attrs__: ClassVar[list[attrs.Attribute]] = []
    _registry: dict[str, type[BaseStage]] = {}
    type: str

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._registry[cls.type] = cls

    @classmethod
    def from_stage_type(cls, id: str) -> BaseStage:
        """Create new instance of appropriate stage from its type."""
        new = cls._registry[str(id)]
        return new()

    @classmethod
    def _from_psstage(cls, psstage: PSMethod, /) -> BaseStage:
        """Generate parameters from dotnet method object."""
        new = cls.from_stage_type(psstage.StageType)
        new._update_params(psstage)
        new._update_params_nested(psstage)
        return new

    def _update_params(self, psstage: PSMethod, /) -> None: ...

    def _update_params_nested(self, psstage: PSMethod, /) -> None:
        """Retrieve and convert dotnet method for nested field parameters."""
        for field in self.__attrs_attrs__:
            attribute = getattr(self, field.name)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_params(psstage)
            except AttributeError:
                pass

    def _update_psmethod(self, psmethod: PSMethod, /) -> PSMethod:
        """Add stage to dotnet method, and update paramaters on dotnet stage."""
        stage_type = getattr(PSMixedMode.EnumMixedModeStageType, self.type)
        psstage = psmethod.AddStage(stage_type)
        self._update_psstage(psstage)
        self._update_psstage_nested(psstage)
        return psstage

    def _update_psstage(self, psstage: PSMethod, /) -> None: ...

    def _update_psstage_nested(self, psstage: PSMethod, /) -> None:
        """Convert and set field parameters on dotnet method."""
        for field in self.__attrs_attrs__:
            attribute = getattr(self, field.name)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_psmethod(psstage)
            except AttributeError:
                pass


@attrs.define(slots=False)
class ConstantE(BaseStage, mixins.CurrentLimitsMixin):
    """Amperometric detection stage."""

    type: Literal['ConstantE'] = 'ConstantE'

    potential: float = 0.0
    """Potential in V."""

    run_time: float = 1.0
    """Run time in s."""

    @override
    def _update_psstage(self, psstage: PSMethod, /):
        psstage.Potential = self.potential
        psstage.RunTime = self.run_time

    @override
    def _update_params(self, psstage: PSMethod, /):
        self.potential = single_to_double(psstage.Potential)
        self.run_time = single_to_double(psstage.RunTime)


@attrs.define(slots=False)
class ConstantI(BaseStage, mixins.PotentialLimitsMixin):
    """Potentiometry stage."""

    type: Literal['ConstantI'] = 'ConstantI'

    current: float = 0.0
    """The current to apply in the given current range.

    Note that this value acts as a multiplier in the applied current range.

    So if 10 uA is the applied current range and 1.5 is given as current value,
    the applied current will be 15 uA."""

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    run_time: float = 1.0
    """Run time in s."""

    @override
    def _update_psstage(self, psstage: PSMethod, /):
        psstage.AppliedCurrentRange = self.applied_current_range._to_psobj()
        psstage.Current = self.current
        psstage.RunTime = self.run_time

    @override
    def _update_params(self, psstage: PSMethod, /):
        self.applied_current_range = CURRENT_RANGE._from_psobj(psstage.AppliedCurrentRange)
        self.current = single_to_double(psstage.Current)
        self.run_time = single_to_double(psstage.RunTime)


@attrs.define(slots=False)
class SweepE(BaseStage, mixins.CurrentLimitsMixin):
    """Linear sweep detection stage."""

    type: Literal['SweepE'] = 'SweepE'

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    scanrate: float = 1.0
    """Scan rate in V/s."""

    @override
    def _update_psstage(self, psstage: PSMethod, /):
        psstage.BeginPotential = self.begin_potential
        psstage.EndPotential = self.end_potential
        psstage.StepPotential = self.step_potential
        psstage.Scanrate = self.scanrate

    @override
    def _update_params(self, psstage: PSMethod, /):
        self.begin_potential = single_to_double(psstage.BeginPotential)
        self.end_potential = single_to_double(psstage.EndPotential)
        self.step_potential = single_to_double(psstage.StepPotential)
        self.scanrate = single_to_double(psstage.Scanrate)


@attrs.define(slots=False)
class OpenCircuit(BaseStage, mixins.PotentialLimitsMixin):
    """Ocp stage."""

    type: Literal['OpenCircuit'] = 'OpenCircuit'

    run_time: float = 1.0
    """Run time in s."""

    @override
    def _update_psstage(self, psstage: PSMethod, /):
        psstage.RunTime = self.run_time

    @override
    def _update_params(self, psstage: PSMethod, /):
        self.run_time = single_to_double(psstage.RunTime)


@attrs.define(slots=False)
class Impedance(BaseStage):
    """Electostatic impedance stage."""

    type: Literal['Impedance'] = 'Impedance'

    run_time: float = 10.0
    """Run time in s."""

    dc_potential: float = 0.0
    """DC potential in V."""

    ac_potential: float = 0.01
    """AC potential in V RMS."""

    frequency: float = 50000.0
    """Frequency in Hz."""

    min_sampling_time: float = 0.5
    """Minimum sampling time in s.

    The instrument will measure at least 2 sine waves.
    The sampling time will be automatically adjusted when necessary."""

    max_equilibration_time: float = 5.0
    """Max equilibration time in s.

    Used as a guard when the frequency drops below 1/max. equilibration time."""

    @override
    def _update_psstage(self, psstage: PSMethod, /):
        psstage.Potential = self.dc_potential
        psstage.Eac = self.ac_potential

        psstage.RunTime = self.run_time
        psstage.FixedFrequency = self.frequency

        psstage.SamplingTime = self.min_sampling_time
        psstage.MaxEqTime = self.max_equilibration_time

    @override
    def _update_params(self, psstage: PSMethod, /):
        self.dc_potential = single_to_double(psstage.Potential)
        self.ac_potential = single_to_double(psstage.Eac)

        self.run_time = single_to_double(psstage.RunTime)
        self.frequency = single_to_double(psstage.FixedFrequency)

        self.min_sampling_time = single_to_double(psstage.SamplingTime)
        self.max_equilibration_time = single_to_double(psstage.MaxEqTime)


@attrs.define
class MixedMode(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create mixed mode method parameters."""

    _id = 'mm'

    interval_time: float = 0.1
    """Interval time in s."""

    cycles: int = 1
    """Number of times to go through all stages."""

    stages: list[ConstantE | ConstantI | SweepE | OpenCircuit | Impedance] = attrs.field(
        factory=list
    )
    """List of stages to run through."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with mixed mode settings."""
        psmethod.nCycles = self.cycles
        psmethod.IntervalTime = self.interval_time

        for stage in self.stages:
            _ = stage._update_psmethod(psmethod)

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.cycles = psmethod.nCycles
        self.interval_time = single_to_double(psmethod.IntervalTime)

        for psstage in psmethod.Stages:
            stage = BaseStage._from_psstage(psstage)

            self.stages.append(stage)  # type: ignore
