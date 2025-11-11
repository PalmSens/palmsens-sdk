from __future__ import annotations

from typing import Literal

import attrs
import PalmSens.Techniques as PSTechniques
from PalmSens import FixedCurrentRange as PSFixedCurrentRange
from PalmSens import FixedPotentialRange as PSFixedPotentialRange
from PalmSens import Method as PSMethod
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType
from typing_extensions import override

from .._shared import single_to_double
from . import mixins
from ._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    ELevel,
    ILevel,
    get_extra_value_mask,
    set_extra_value_mask,
)
from .base import BaseTechnique


@attrs.define
class CyclicVoltammetry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create cyclic voltammetry method parameters."""

    _id = 'cv'

    equilibration_time: float = 0.0
    """Equilibration time in s"""

    begin_potential: float = -0.5
    """Begin potential in V"""

    vertex1_potential: float = 0.5
    """Vertex 1 potential in V"""

    vertex2_potential: float = -0.5
    """Vertex 2 potential in V"""

    step_potential: float = 0.1
    """Step potential in V"""

    scanrate: float = 1.0
    """Scan rate in V/s"""

    n_scans: int = 1
    """Number of scans"""

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast cyclic voltammetry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.Vtx1Potential = self.vertex1_potential
        psmethod.Vtx2Potential = self.vertex2_potential
        psmethod.StepPotential = self.step_potential
        psmethod.Scanrate = self.scanrate
        psmethod.nScans = self.n_scans

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.vertex1_potential = single_to_double(psmethod.Vtx1Potential)
        self.vertex2_potential = single_to_double(psmethod.Vtx2Potential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.scanrate = single_to_double(psmethod.Scanrate)
        self.n_scans = psmethod.nScans

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class FastCyclicVoltammetry(
    BaseTechnique,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.IrDropCompensationMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create fast cyclic voltammetry method parameters."""

    _id = 'fcv'

    current_range: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    """Fixed current range."""

    equilibration_time: float = 0.0
    """Equilibration time in s"""

    begin_potential: float = -0.5
    """Begin potential in V"""

    vertex1_potential: float = 0.5
    """Vertex 1 potential in V"""

    vertex2_potential: float = -0.5
    """Vertex 2 potential in V"""

    step_potential: float = 0.01
    """Step potential in V"""

    scanrate: float = 500.0
    """Scan rate in V/s"""

    n_scans: int = 1
    """Number of scans"""

    n_avg_scans: int = 1
    """Number of scans to be averaged."""

    n_equil_scans: int = 1
    """Number of equilibration scans."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast cyclic voltammetry settings."""

        psmethod.Ranging = PSFixedCurrentRange(self.current_range._to_psobj())
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.Vtx1Potential = self.vertex1_potential
        psmethod.Vtx2Potential = self.vertex2_potential
        psmethod.StepPotential = self.step_potential
        psmethod.Scanrate = self.scanrate
        psmethod.nScans = self.n_scans
        psmethod.nAvgScans = self.n_avg_scans
        psmethod.nEqScans = self.n_equil_scans

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.current_range = CURRENT_RANGE._from_psobj(psmethod.Ranging.StartCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.vertex1_potential = single_to_double(psmethod.Vtx1Potential)
        self.vertex2_potential = single_to_double(psmethod.Vtx2Potential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.scanrate = single_to_double(psmethod.Scanrate)
        self.n_scans = psmethod.nScans
        self.n_avg_scans = psmethod.nAvgScans
        self.n_equil_scans = psmethod.nEqScans


@attrs.define
class ACVoltammetry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create AC Voltammetry method parameters."""

    _id = 'acv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    ac_potential: float = 0.01
    """Sine wave amplitude in V as rms value."""

    frequency: float = 100.0
    """AC frequency in HZ."""

    scanrate: float = 1.0
    """Scan rate in V/s."""

    measure_dc_current: bool = False
    """Measure the DC current seperately."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with linear sweep settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.EndPotential = self.end_potential
        psmethod.StepPotential = self.step_potential
        psmethod.Frequency = self.frequency
        psmethod.SineWaveAmplitude = self.ac_potential
        psmethod.MeasureDCcurrent = self.measure_dc_current
        psmethod.Scanrate = self.scanrate

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.end_potential = single_to_double(psmethod.EndPotential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.ac_potential = single_to_double(psmethod.SineWaveAmplitude)
        self.frequency = single_to_double(psmethod.Frequency)
        self.scanrate = single_to_double(psmethod.Scanrate)
        self.measure_dc_current = psmethod.MeasureDCcurrent


@attrs.define
class LinearSweepVoltammetry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create linear sweep method parameters."""

    _id = 'lsv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    scanrate: float = 1.0
    """Scan rate in V/s."""

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with linear sweep settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.EndPotential = self.end_potential
        psmethod.StepPotential = self.step_potential
        psmethod.Scanrate = self.scanrate

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.end_potential = single_to_double(psmethod.EndPotential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.scanrate = single_to_double(psmethod.Scanrate)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class SquareWaveVoltammetry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create square wave method parameters."""

    _id = 'swv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    frequency: float = 10.0
    """Frequency in Hz."""

    amplitude: float = 0.05
    """Amplitude in V as half peak-to-peak value."""

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    record_forward_and_reverse_currents: bool = False
    """Record forward and reverse currents"""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with square wave voltammetry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.EndPotential = self.end_potential
        psmethod.StepPotential = self.step_potential
        psmethod.Frequency = self.frequency
        psmethod.PulseAmplitude = self.amplitude

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
            record_forward_and_reverse_currents=self.record_forward_and_reverse_currents,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.end_potential = single_to_double(psmethod.EndPotential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.frequency = single_to_double(psmethod.Frequency)
        self.amplitude = single_to_double(psmethod.PulseAmplitude)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
            'record_forward_and_reverse_currents',
        ):
            setattr(self, key, msk[key])


@attrs.define
class DifferentialPulseVoltammetry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create differential pulse voltammetry method parameters."""

    _id = 'dpv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    pulse_potential: float = 0.05
    """Pulse potential in V."""

    pulse_time: float = 0.01
    """Pulse time in s."""

    scan_rate: float = 1.0
    """Scan rate (potential/time) in V/s."""

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with linear sweep settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.EndPotential = self.end_potential
        psmethod.StepPotential = self.step_potential
        psmethod.PulsePotential = self.pulse_potential
        psmethod.PulseTime = self.pulse_time
        psmethod.Scanrate = self.scan_rate

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.end_potential = single_to_double(psmethod.EndPotential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.pulse_potential = single_to_double(psmethod.PulsePotential)
        self.pulse_time = single_to_double(psmethod.PulseTime)
        self.scan_rate = single_to_double(psmethod.Scanrate)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class NormalPulseVoltammetry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create normal pulse voltammetry method parameters."""

    _id = 'npv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Begin potential in V."""

    end_potential: float = 0.5
    """End potential in V."""

    step_potential: float = 0.1
    """Step potential in V."""

    pulse_time: float = 0.01
    """Pulse time in s."""

    scan_rate: float = 1.0
    """Scan rate (potential/time) in V/s."""

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with normal pulse voltammetry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.BeginPotential = self.begin_potential
        psmethod.EndPotential = self.end_potential
        psmethod.StepPotential = self.step_potential
        psmethod.PulseTime = self.pulse_time
        psmethod.Scanrate = self.scan_rate

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.end_potential = single_to_double(psmethod.EndPotential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.pulse_time = single_to_double(psmethod.PulseTime)
        self.scan_rate = single_to_double(psmethod.Scanrate)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ChronoAmperometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.ChargeLimitsMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create chrono amperometry method parameters."""

    _id = 'ad'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """Interval time in s."""

    potential: float = 0.0
    """Potential in V."""

    run_time: float = 1.0
    """Run time in s."""

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with chrono amperometry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.IntervalTime = self.interval_time
        psmethod.Potential = self.potential
        psmethod.RunTime = self.run_time

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.potential = single_to_double(psmethod.Potential)
        self.run_time = single_to_double(psmethod.RunTime)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class FastAmperometry(
    BaseTechnique,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.ChargeLimitsMixin,
    mixins.IrDropCompensationMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create fast amperometry method parameters."""

    _id = 'fam'

    current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_nA
    """Fixed current range."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    equilibration_potential: float = 1.0
    """Equilibration potential in V."""

    interval_time: float = 0.1
    """Interval time in s."""

    potential: float = 0.5
    """Potential in V."""

    run_time: float = 1.0
    """Run time in s."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast amperometry settings."""
        psmethod.Ranging = PSFixedCurrentRange(self.current_range._to_psobj())
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.EqPotentialFA = self.equilibration_potential
        psmethod.IntervalTime = self.interval_time
        psmethod.Potential = self.potential
        psmethod.RunTime = self.run_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.current_range = CURRENT_RANGE._from_psobj(psmethod.Ranging.StartCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.equilibration_potential = single_to_double(psmethod.EqPotentialFA)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.potential = single_to_double(psmethod.Potential)
        self.run_time = single_to_double(psmethod.RunTime)


@attrs.define
class MultiStepAmperometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.IrDropCompensationMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create multi-step amperometry method parameters."""

    _id = 'ma'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """Interval time in s."""

    n_cycles: int = 1
    """Number of cycles."""

    levels: list[ELevel] = attrs.field(factory=lambda: [ELevel()])
    """List of levels.

    Use `ELevel()` to create levels.
    """

    enable_bipot_current: bool = False
    """Enable bipot current."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with multistep amperometry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.IntervalTime = self.interval_time
        psmethod.nCycles = self.n_cycles
        psmethod.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            psmethod.Levels.Add(level.to_psobj())

        psmethod.UseSelectiveRecord = any(level.record for level in self.levels)
        psmethod.UseLimits = any(level.use_limits for level in self.levels)

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.n_cycles = psmethod.nCycles

        self.levels = [ELevel.from_psobj(pslevel) for pslevel in psmethod.Levels]

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class PulsedAmperometricDetection(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DelayTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create pulsed amperometric detection method parameters."""

    _id = 'pad'

    _MODES: tuple[Literal['dc', 'pulse', 'differential'], ...] = ('dc', 'pulse', 'differential')

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    potential: float = 0.5
    """Potential in V."""

    pulse_potential: float = 0.05
    """Pulse potential in V."""

    pulse_time: float = 0.01
    """Pulse time in s."""

    mode: Literal['dc', 'pulse', 'differential'] = 'dc'
    """Measurement mode.

    - dc: Measurement is performed at potential (E dc)
    - pulse: measurement is performed at pulse potential (E pulse)
    - differential: measurement is (pulse - dc)
    """

    interval_time: float = 0.1
    """Interval time in s."""

    run_time: float = 10.0
    """Run time in s."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with pulsed amperometric detection settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.IntervalTime = self.interval_time
        psmethod.PulseTime = self.pulse_time
        psmethod.PulsePotentialAD = self.pulse_potential
        psmethod.Potential = self.potential
        psmethod.RunTime = self.run_time

        mode = self._MODES.index(self.mode) + 1
        psmethod.tMode = PSTechniques.PulsedAmpDetection.enumMode(mode)

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.potential = single_to_double(psmethod.Potential)
        self.pulse_potential = single_to_double(psmethod.PulsePotentialAD)
        self.pulse_time = single_to_double(psmethod.PulseTime)
        self.run_time = single_to_double(psmethod.RunTime)

        self.mode = self._MODES[int(psmethod.tMode) - 1]


@attrs.define
class MultiplePulseAmperometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create multiple pulse amperometry method parameters."""

    _id = 'mpad'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    run_time: float = 10.0
    """Run time in s."""

    duration_1: float = 0.1
    """Duration of the first applied potential in s."""

    duration_2: float = 0.1
    """Duration of the first applied potential in s."""

    duration_3: float = 0.1
    """Duration of the first applied potential in s."""

    potential_1: float = 0.0
    """First applied potential level at which the current is recorded in V."""

    potential_2: float = 0.0
    """Second applied potential level at which the current is recorded in V."""

    potential_3: float = 0.0
    """Third applied potential level at which the current is recorded in V."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with multistep amperometry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.RunTime = self.run_time

        psmethod.E1 = self.potential_1
        psmethod.E2 = self.potential_2
        psmethod.E3 = self.potential_3
        psmethod.t1 = self.duration_1
        psmethod.t2 = self.duration_2
        psmethod.t3 = self.duration_3

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.run_time = single_to_double(psmethod.RunTime)

        self.potential_1 = single_to_double(psmethod.E1)
        self.potential_2 = single_to_double(psmethod.E2)
        self.potential_3 = single_to_double(psmethod.E3)
        self.duration_1 = single_to_double(psmethod.t1)
        self.duration_2 = single_to_double(psmethod.t2)
        self.duration_3 = single_to_double(psmethod.t3)


@attrs.define
class OpenCircuitPotentiometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create open circuit potentiometry method parameters."""

    _id = 'ocp'

    interval_time: float = 0.1
    """Interval time in s."""

    run_time: float = 1.0
    """Run time in s."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record working electrode current."""

    record_we_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    """Record working electrode current range.

    Use `CURRENT_RANGE` to define the range."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with open circuit potentiometry settings."""
        psmethod.IntervalTime = self.interval_time
        psmethod.RunTime = self.run_time
        psmethod.AppliedCurrentRange = self.record_we_current_range._to_psobj()

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.run_time = single_to_double(psmethod.RunTime)
        self.record_we_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ChronoPotentiometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create potentiometry method parameters."""

    _id = 'pot'

    current: float = 0.0
    """The current to apply in the given current range.

    Note that this value acts as a multiplier in the applied current range.

    So if 10 uA is the applied current range and 1.5 is given as current value,
    the applied current will be 15 uA."""

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    interval_time: float = 0.1
    """Interval time in s (default: 0.1)"""

    run_time: float = 1.0
    """Run time in s."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_current: bool = False
    """Record working electrode current."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with chronopotentiometry settings."""
        psmethod.Current = self.current
        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()
        psmethod.IntervalTime = self.interval_time
        psmethod.RunTime = self.run_time

        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.current = single_to_double(psmethod.Current)
        self.applied_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.run_time = single_to_double(psmethod.RunTime)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class StrippingChronoPotentiometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create stripping potentiometry method parameters.

    If the stripping current is set to 0, then chemical stripping is performed,
    otherwise it is chemical constant current stripping.
    The applicable range is +- 0.001 microampere to +- 2 milliampere.
    """

    _id = 'scp'

    potential_range: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_500_mV
    """Fixed potential range."""

    current: float = 0.0
    """The stripping current to apply in the given current range.

    Note that this value acts as a multiplier in the applied current range.

    So if 10 uA is the applied current range and 1.5 is given as current value,
    the applied current will be 15 uA."""

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    end_potential: float = 0.0
    """Potential in V where measurement ends."""

    measurement_time: float = 1.0
    """Measurement time in s."""

    bandwidth: None | float = None
    """Override the bandwidth filter cutoff frequency (in Hz)."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with stripping chrono potentiometry settings."""
        psmethod.RangingPotential = PSFixedPotentialRange(self.potential_range._to_psobj())

        psmethod.Current = self.current
        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()
        psmethod.MeasurementTime = self.measurement_time
        psmethod.EndPotential = self.end_potential

        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()

        if self.bandwidth is not None:
            psmethod.OverrideBandwidth = True
            psmethod.Bandwidth = self.bandwidth

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.potential_range = POTENTIAL_RANGE._from_psobj(
            psmethod.RangingPotential.StartPotentialRange
        )

        self.current = single_to_double(psmethod.Current)
        self.applied_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)
        self.measurement_time = single_to_double(psmethod.MeasurementTime)
        self.end_potential = single_to_double(psmethod.EndPotential)

        if psmethod.OverrideBandwidth:
            self.bandwidth = single_to_double(psmethod.Bandwidth)


@attrs.define
class LinearSweepPotentiometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DelayTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create linear sweep potentiometry method parameters."""

    _id = 'lsp'

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    current_begin: float = -1.0
    """Current applied at beginning of measurement.

    This value is multiplied by the defined current range."""

    current_end: float = 1.0
    """Current applied at end of measurement.

    This value is multiplied by the defined current range."""

    current_step: float = 0.01
    """Current step.

    This value is multiplied by the defined current range."""

    scan_rate: float = 1.0
    """The applied scan rate.

    This value is multiplied by the defined current range."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record working electrode current."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with lineas sweep potentiometry settings."""
        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()

        psmethod.BeginCurrent = self.current_begin
        psmethod.EndCurrent = self.current_end
        psmethod.StepCurrent = self.current_step
        psmethod.ScanrateG = self.scan_rate

        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)

        self.current_begin = single_to_double(psmethod.BeginCurrent)
        self.current_end = single_to_double(psmethod.EndCurrent)
        self.current_step = single_to_double(psmethod.StepCurrent)
        self.scan_rate = single_to_double(psmethod.ScanrateG)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class MultiStepPotentiometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create multi-step potentiometry method parameters."""

    _id = 'mp'

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    interval_time: float = 0.1
    """Interval time in s."""

    n_cycles: int = 1
    """Number of cycles."""

    levels: list[ILevel] = attrs.field(factory=lambda: [ILevel()])
    """List of levels.

    Use `ILevel()` to create levels.
    """

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with multistep potentiometry settings."""
        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()
        psmethod.IntervalTime = self.interval_time
        psmethod.nCycles = self.n_cycles
        psmethod.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            psmethod.Levels.Add(level.to_psobj())

        psmethod.UseSelectiveRecord = any(level.record for level in self.levels)
        psmethod.UseLimits = any(level.use_limits for level in self.levels)

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)

        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.n_cycles = psmethod.nCycles

        self.levels = [ILevel.from_psobj(pslevel) for pslevel in psmethod.Levels]

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ChronoCoulometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.ChargeLimitsMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create linear sweep method parameters."""

    _id = 'cc'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """Interval time in s."""

    step1_potential: float = 0.5
    """Potential applied during first step in V."""

    step1_run_time: float = 5.0
    """Run time for the first step."""

    step2_potential: float = 0.5
    """Potential applied during second step in V."""

    step2_run_time: float = 5.0
    """Run time for the second step."""

    bandwidth: None | float = None
    """Override bandwidth on MethodSCRIPT devices if set."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with chrono coulometry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.IntervalTime = self.interval_time

        psmethod.EFirstStep = self.step1_potential
        psmethod.ESecondStep = self.step2_potential
        psmethod.TFirstStep = self.step1_run_time
        psmethod.TSecondStep = self.step2_run_time

        if self.bandwidth is not None:
            psmethod.OverrideBandwidth = True
            psmethod.Bandwidth = self.bandwidth

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.step1_potential = single_to_double(psmethod.EFirstStep)
        self.step2_potential = single_to_double(psmethod.ESecondStep)
        self.step1_run_time = single_to_double(psmethod.TFirstStep)
        self.step2_run_time = single_to_double(psmethod.TSecondStep)

        if psmethod.OverrideBandwidth:
            self.bandwidth = single_to_double(psmethod.Bandwidth)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ElectrochemicalImpedanceSpectroscopy(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.MeasurementTriggersMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create potentiometry method parameters."""

    _id = 'eis'

    _SCAN_TYPES: tuple[Literal['potential', 'time', 'fixed'], ...] = (
        'potential',
        'time',
        'fixed',
    )
    _FREQ_TYPES: tuple[Literal['fixed', 'scan'], ...] = ('fixed', 'scan')

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    dc_potential: float = 0.0
    """DC potential in V."""

    ac_potential: float = 0.01
    """AC potential in V RMS."""

    n_frequencies: int = 11
    """Number of frequencies."""

    max_frequency: float = 1e5
    """Maximum frequency in Hz."""

    min_frequency: float = 1e3
    """Minimum frequency in Hz."""

    scan_type: Literal['potential', 'time', 'fixed'] = 'fixed'
    """Whether a single or multiple frequency scans are performed.

    Possible values: 'potential', 'time', 'fixed'.

    * Fixed scan: perform a single scan (default).
    * Time scan: scans are repeated for a specific amount of time at a specific interval.
    * Potential scan: scans are repeated over a range of DC potential values.
      A potential scan should not be performed versus the OCP.
    """

    frequency_type: Literal['fixed', 'scan'] = 'scan'
    """Whether to measure a single frequency or scan over a range of frequencies.

    Possible values: 'scan', 'fixed'.

    Scan: multiple frequency
    Fixed: single frequency. This can be used in combination with a time or a potential scan.
    """

    run_time: float = 10.0
    """This is the minimal run time in seconds (time scan only).

    For example, if a frequency scan takes 18 seconds and is measured
    at an interval of 19 seconds for a `run_time` of 40 seconds, then
    three iterations will be performed."""

    interval_time: float = 0.1
    """The interval at which a measurement iteration should be performed (time scan only).

    If a measurement iteration takes longer than the interval time the next measurement
    will not be triggered until after it has been completed.
    """

    begin_potential: float = 0.0
    """Begin potential in V (potential scan only).

    The DC potential of the applied sine wave to start the series of iterative measurements at.
    """

    end_potential: float = 0.0
    """End potential in V (potential scan only).

    The DC potential of the applied sine wave at which the series of iterative measurements ends.
    """

    step_potential: float = 0.01
    """Step potential in V (potential scan only).

    The size of DC potential step to iterate with.
    """

    min_sampling_time: float = 0.5
    """Minimum sampling time in s.

    Each measurement point of the impedance spectrum is performed
    during the period specified by SamplingTime.

    This means that the number of measured sine waves is equal to SamplingTime * frequency.
    If this value is less than 1 sine wave, the sampling is extended to 1 / frequency.

    So for a measurement at a frequency, at least one complete sine wave is measured.
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
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with electrochemical impedance spectroscopy settings."""

        if self.scan_type == 'potential':
            psmethod.BeginPotential = self.begin_potential
            psmethod.EndPotential = self.end_potential
            psmethod.StepPotential = self.step_potential
        elif self.scan_type == 'time':
            psmethod.RunTime = self.run_time
            psmethod.IntervalTime = self.interval_time

        psmethod.ScanType = enumScanType(self._SCAN_TYPES.index(self.scan_type))
        psmethod.FreqType = enumFrequencyType(self._FREQ_TYPES.index(self.frequency_type))
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.Potential = self.dc_potential
        psmethod.Eac = self.ac_potential
        psmethod.nFrequencies = self.n_frequencies
        psmethod.MaxFrequency = self.max_frequency
        psmethod.MinFrequency = self.min_frequency
        psmethod.SamplingTime = self.min_sampling_time
        psmethod.MaxEqTime = self.max_equilibration_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.scan_type = self._SCAN_TYPES[int(psmethod.ScanType)]
        self.frequency_type = self._FREQ_TYPES[int(psmethod.FreqType)]
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.dc_potential = single_to_double(psmethod.Potential)
        self.ac_potential = single_to_double(psmethod.Eac)
        self.n_frequencies = psmethod.nFrequencies
        self.max_frequency = single_to_double(psmethod.MaxFrequency)
        self.min_frequency = single_to_double(psmethod.MinFrequency)

        if self.scan_type == 'potential':
            self.begin_potential = single_to_double(psmethod.BeginPotential)
            self.end_potential = single_to_double(psmethod.EndPotential)
            self.step_potential = single_to_double(psmethod.StepPotential)
        elif self.scan_type == 'time':
            self.run_time = single_to_double(psmethod.RunTime)
            self.interval_time = single_to_double(psmethod.IntervalTime)


@attrs.define
class FastImpedanceSpectroscopy(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.MeasurementTriggersMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.GeneralMixin,
):
    """Create fast impedance spectroscopy method parameters."""

    _id = 'fis'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """Interval time in s."""

    run_time: float = 10.0
    """Run time in s."""

    dc_potential: float = 0.0
    """Potential applied during measurement in V."""

    ac_potential: float = 0.01
    """Potential amplitude in V (rms)."""

    frequency: float = 50000.0
    """Frequency in Hz."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fas impedance spectroscopy settings."""
        psmethod.Eac = self.ac_potential
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.FixedFrequency = self.frequency
        psmethod.IntervalTime = self.interval_time
        psmethod.Potential = self.dc_potential
        psmethod.RunTime = self.run_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.ac_potential = single_to_double(psmethod.Eac)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.frequency = single_to_double(psmethod.FixedFrequency)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.dc_potential = single_to_double(psmethod.Potential)
        self.run_time = single_to_double(psmethod.RunTime)


@attrs.define
class GalvanostaticImpedanceSpectroscopy(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
):
    """Create potentiometry method parameters."""

    _id = 'gis'

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    ac_current: float = 0.01
    """AC current in applied current range RMS."""

    dc_current: float = 0.0
    """DC current in applied current range."""

    n_frequencies: int = 11
    """Number of frequencies."""

    max_frequency: float = 1e5
    """Maximum frequency in Hz."""

    min_frequency: float = 1e3
    """Minimum frequency in Hz."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with galvanic impedance spectroscopy settings."""

        psmethod.ScanType = enumScanType.Fixed
        psmethod.FreqType = enumFrequencyType.Scan
        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.Iac = self.ac_current
        psmethod.Idc = self.dc_current
        psmethod.nFrequencies = self.n_frequencies
        psmethod.MaxFrequency = self.max_frequency
        psmethod.MinFrequency = self.min_frequency

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.ac_current = single_to_double(psmethod.Iac)
        self.dc_current = single_to_double(psmethod.Idc)
        self.n_frequencies = psmethod.nFrequencies
        self.max_frequency = single_to_double(psmethod.MaxFrequency)
        self.min_frequency = single_to_double(psmethod.MinFrequency)


@attrs.define
class FastGalvanostaticImpedanceSpectroscopy(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.GeneralMixin,
):
    """Create fast galvanostatic impededance spectroscopy method parameters."""

    _id = 'fgis'

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    run_time: float = 10.0
    """Run time in s."""

    interval_time: float = 0.1
    """Interval time in s."""

    ac_current: float = 0.01
    """AC current in applied current range RMS.

    This value is multiplied by the applied current range."""

    dc_current: float = 0.0
    """DC current in applied current range.

    This value is multiplied by the applied current range."""

    frequency: float = 50000.0
    """Frequency in Hz."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast galvanic impedance spectroscopy settings."""
        psmethod.AppliedCurrentRange = self.applied_current_range._to_psobj()
        psmethod.Iac = self.ac_current
        psmethod.Idc = self.dc_current
        psmethod.FixedFrequency = self.frequency
        psmethod.RunTime = self.run_time
        psmethod.IntervalTime = self.interval_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = CURRENT_RANGE._from_psobj(psmethod.AppliedCurrentRange)
        self.ac_current = single_to_double(psmethod.Iac)
        self.dc_current = single_to_double(psmethod.Idc)
        self.frequency = single_to_double(psmethod.FixedFrequency)
        self.run_time = single_to_double(psmethod.RunTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)


@attrs.define
class MethodScript(BaseTechnique):
    """Create a method script sandbox object."""

    _id = 'ms'

    script: str = """e
wait 100m
if 1 < 2
    send_string "Hello world"
endif

"""
    """Script to run.

    For more info on MethodSCRIPT, see:
        https://www.palmsens.com/methodscript/ for more information."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with MethodScript."""
        psmethod.MethodScript = self.script

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.script = psmethod.MethodScript
