from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

import attrs
from PalmSens.Techniques import MixedMode as PSMixedMode

from pypalmsens._shared import single_to_double

from ._shared import (
    CURRENT_RANGE,
)
from .techniques import (
    CurrentLimitsMixin,
    CurrentRangeMixin,
    DataProcessingMixin,
    GeneralMixin,
    MethodSettings,
    PostMeasurementMixin,
    PotentialLimitsMixin,
    PretreatmentMixin,
)


@runtime_checkable
class StageProtocol(Protocol):
    """Protocol to provide base methods for stage classes."""

    __attrs_attrs__: ClassVar[list[attrs.Attribute]] = []

    def _update_attributes(self, *, obj):
        for field in self.__attrs_attrs__:
            attribute = getattr(self, field.name)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_psmethod(obj=obj)
            except AttributeError:
                pass

    def _update_stage_params(self, *, obj):
        for field in self.__attrs_attrs__:
            attribute = getattr(self, field.name)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_params(obj=obj)
            except AttributeError:
                pass


@attrs.define(slots=False)
class ConstantE(StageProtocol, CurrentLimitsMixin):
    """Amperometric detection stage."""

    _type = PSMixedMode.EnumMixedModeStageType.ConstantE

    potential: float = 0.0
    """Potential in V."""

    run_time: float = 1.0
    """Run time in s."""

    def _update_psobj(self, *, obj):
        obj.Potential = self.potential
        obj.RunTime = self.run_time

        self._update_attributes(obj=obj)

    def _update_stage(self, *, obj):
        self.potential = single_to_double(obj.Potential)
        self.run_time = single_to_double(obj.RunTime)

        self._update_stage_params(obj=obj)


@attrs.define(slots=False)
class ConstantI(StageProtocol, PotentialLimitsMixin):
    """Potentiometry stage."""

    _type = PSMixedMode.EnumMixedModeStageType.ConstantI

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

    def _update_psobj(self, *, obj):
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()
        obj.Current = self.current
        obj.RunTime = self.run_time

        self._update_attributes(obj=obj)

    def _update_stage(self, *, obj):
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)
        self.current = single_to_double(obj.Current)
        self.run_time = single_to_double(obj.RunTime)

        self._update_stage_params(obj=obj)


@attrs.define(slots=False)
class SweepE(StageProtocol, CurrentLimitsMixin):
    """Linear sweep detection stage."""

    _type = PSMixedMode.EnumMixedModeStageType.SweepE

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    scanrate: float = 1.0
    """Scan rate in V/s."""

    def _update_psobj(self, *, obj):
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate

        self._update_attributes(obj=obj)

    def _update_stage(self, *, obj):
        self.begin_potential = single_to_double(obj.BeginPotential)
        self.end_potential = single_to_double(obj.EndPotential)
        self.step_potential = single_to_double(obj.StepPotential)
        self.scanrate = single_to_double(obj.Scanrate)

        self._update_stage_params(obj=obj)


@attrs.define(slots=False)
class OpenCircuit(StageProtocol, PotentialLimitsMixin):
    """Ocp stage."""

    _type = PSMixedMode.EnumMixedModeStageType.OpenCircuit

    run_time: float = 1.0
    """Run time in s."""

    def _update_psobj(self, *, obj):
        obj.RunTime = self.run_time

        self._update_attributes(obj=obj)

    def _update_stage(self, *, obj):
        self.run_time = single_to_double(obj.RunTime)

        self._update_stage_params(obj=obj)


@attrs.define(slots=False)
class Impedance(StageProtocol):
    """Electostatic impedance stage."""

    _type = PSMixedMode.EnumMixedModeStageType.Impedance

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

    The instrument will measure at leas 2 sine waves.
    The sampling time will be automatically adjusted when necessary."""

    max_equilibration_time: float = 5.0
    """Max equilibration time in s.

    Used as a guard when the frequency drops below 1/max. equilibration time."""

    def _update_psobj(self, *, obj):
        obj.Potential = self.dc_potential
        obj.Eac = self.ac_potential

        obj.RunTime = self.run_time
        obj.FixedFrequency = self.frequency

        obj.SamplingTime = self.min_sampling_time
        obj.MaxEqTime = self.max_equilibration_time

        self._update_attributes(obj=obj)

    def _update_stage(self, *, obj):
        self.dc_potential = single_to_double(obj.Potential)
        self.ac_potential = single_to_double(obj.Eac)

        self.run_time = single_to_double(obj.RunTime)
        self.frequency = single_to_double(obj.FixedFrequency)

        self.min_sampling_time = single_to_double(obj.SamplingTime)
        self.max_equilibration_time = single_to_double(obj.MaxEqTime)

        self._update_stage_params(obj=obj)


TStage = ConstantE | ConstantI | SweepE | OpenCircuit | Impedance


@attrs.define
class MixedMode(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    DataProcessingMixin,
    GeneralMixin,
):
    """Create mixed mode method parameters."""

    _id = 'mm'

    interval_time: float = 0.1
    """Interval time in s."""

    cycles: int = 1
    """Number of times to go through all stages."""

    stages: list[TStage] = attrs.field(factory=list)
    """List of stages to run through."""

    def _update_psmethod(self, *, obj):
        """Update method with mixed mode settings."""
        obj.nCycles = self.cycles
        obj.IntervalTime = self.interval_time

        for stage in self.stages:
            psstage = obj.AddStage(stage._type)

            stage._update_psobj(obj=psstage)

    def _update_params(self, *, obj):
        self.cycles = obj.nCycles
        self.interval_time = single_to_double(obj.IntervalTime)

        for psstage in obj.Stages:
            match psstage.StageType:
                case ConstantE._type:
                    Stage = ConstantE
                case ConstantI._type:
                    Stage = ConstantI
                case SweepE._type:
                    Stage = SweepE
                case OpenCircuit._type:
                    Stage = OpenCircuit
                case Impedance._type:
                    Stage = Impedance
                case _:
                    raise ValueError(f'No such stage {psstage.StageType}')

            stage = Stage()
            stage._update_stage(obj=psstage)

            self.stages.append(stage)
