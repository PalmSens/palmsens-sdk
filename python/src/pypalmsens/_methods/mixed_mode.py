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
    """Amperometric detection stage.

    Apply constant potential during this stage."""

    type: Literal['ConstantE'] = 'ConstantE'

    potential: float = 0.0
    """Potential during measurement in V."""

    run_time: float = 1.0
    """Run time of the stage in s."""

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
    """Potentiometry stage.

    Apply constant fixed current during this stage."""

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
    """Run time of the stage in s."""

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
    """Linear sweep detection stage.

    Ramp the voltage from `begin_potential` to `end_potential` during this stage."""

    type: Literal['SweepE'] = 'SweepE'

    begin_potential: float = -0.5
    """Potential where the scan starts in V."""

    end_potential: float = 0.5
    """Potential where the scan stops in V."""

    step_potential: float = 0.1
    """Potential step in V."""

    scanrate: float = 1.0
    """The applied scan rate.  in V/s.

    The applicable range depends on the value of `step_potential`
    since the data acquisition rate is limited by the connected
    instrument.
    """

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
    """Open Circuit stage.

    Measure the open circuit potential during this stage."""

    type: Literal['OpenCircuit'] = 'OpenCircuit'

    run_time: float = 1.0
    """Run time of the stage in s."""

    @override
    def _update_psstage(self, psstage: PSMethod, /):
        psstage.RunTime = self.run_time

    @override
    def _update_params(self, psstage: PSMethod, /):
        self.run_time = single_to_double(psstage.RunTime)


@attrs.define(slots=False)
class Impedance(BaseStage):
    """Electostatic impedance stage.

    This is like EIS with a single frequency step
    (`scan_type = 'fixed'`, `freq_type = 'fixed'`).
    """

    type: Literal['Impedance'] = 'Impedance'

    run_time: float = 10.0
    """Run time of the scan in s."""

    dc_potential: float = 0.0
    """DC potential applied during the scan in V."""

    ac_potential: float = 0.01
    """AC potential in V RMS.

    The amplitude of the AC signal has a range of 0.0001 V to 0.25 V
    (RMS). In many applications, a value of 0.010 V (RMS) is used. The
    actual amplitude must be small enough to prevent a current response
    with considerable higher harmonics of the applied ac frequency.
    """

    frequency: float = 50000.0
    """Fixed frequency in Hz."""

    min_sampling_time: float = 0.5
    """Minimum sampling time in s.

    Each measurement point of the impedance spectrum is performed
    during the period specified by `min_sampling_time`.

    This means that the number of measured sine waves is equal to `min_sampling_time * frequency`.
    If this value is less than 1 sine wave, the sampling is extended to `1 / frequency`.

    So for a measurement at a `frequency`, at least one complete sine wave is measured.
    Reasonable values for the sampling are in the range of 0.1 to 1 s."""

    max_equilibration_time: float = 5.0
    """Max equilibration time in s.

    The EIS measurement requires a stationary state.
    This means that before the actual measurement starts, the sine wave is
    applied during `max_equilibration_time` only to reach the stationary state.

    The maximum number of equilibration sine waves is however 5.

    The minimum number of equilibration sines is set to 1, but for very
    low frequencies, this time is limited by `max_equilibration_time`.

    The maximum time to wait for stationary state is determined by the
    value of this parameter. A reasonable value might be 5 seconds.
    In this case this parameter is only relevant when the lowest frequency
    is less than 1/5 s so 0.2 Hz.
    """

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
    """Create mixed mode method parameters.

    Mixed mode is a flexible technique that allows for switching between potentiostatic,
    galvanostatic, and open circuit measurements during a single run.

    The mixed mode uses different stages similar to the levels during Multistep Amperometry or
    Potentiometry, but each stage can be galvanostatic or potentiostatic independent of the
    previous stage.

    The available stage types are `ConstantE`, `ConstantI`, `SweepE`, `OpenCircuit` and `Impedance`.

    - `ConstantE`: Apply constant potential
    - `ConstantI`: Apply constant current
    - `SweepE`: potential linear sweep (ramp) similar to a regular LSV step
    - `OpenCircuit`: Measure the OCP value
    - `Impedance`: the impedance is measured by applying a small AC potential superimposed with a DC
    potential. This corresponds to an EIS single frequency step (`scan_type = 'fixed'`, `freq_type = 'fixed'`)

    Each stage can use the previous stage’s potential as a reference point, for example, a constant
    current is applied for a fixed period and afterward, the reached potential is kept constant for a
    fixed period.

    Furthermore, each stage can end because a fixed period has elapsed, or certain criteria are
    met. Available criteria include reaching a maximum current, minimum current, maximum
    potential, and minimum potential.
    """

    _id = 'mm'

    interval_time: float = 0.1
    """Time between two samples in s."""

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
