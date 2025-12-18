from __future__ import annotations

from typing import ClassVar, Literal

import PalmSens.Techniques as PSTechniques
from PalmSens import FixedCurrentRange as PSFixedCurrentRange
from PalmSens import FixedPotentialRange as PSFixedPotentialRange
from PalmSens import Method as PSMethod
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType
from pydantic import Field
from typing_extensions import override

from .._shared import single_to_double
from . import mixins
from ._shared import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
    ELevel,
    ILevel,
    cr_enum_to_string,
    cr_string_to_enum,
    get_extra_value_mask,
    pr_enum_to_string,
    pr_string_to_enum,
    set_extra_value_mask,
)
from .base import BaseTechnique


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
    """Create cyclic voltammetry method parameters.

    In Cyclic Voltammetry, recurrent potential scans are performed between the potentials `vertex1_potential`
    and `vertex2_potential` going back the number of times determined by the `n_scans`.
    The scan starts at the `begin_potential` which can be at one of these vertex potentials
    or anywhere in between. The experiment will always terminate at the same potential set as the
    'begin_potential'.
    """

    id: ClassVar[str] = 'cv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts and stops at in V."""

    vertex1_potential: float = 0.5
    """First potential where direction reverses in V."""

    vertex2_potential: float = -0.5
    """Second potential where direction reverses. V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    scanrate: float = 1.0
    """Scan rate in V/s.

    The applicable range depends on the value of `step_potential`."""

    n_scans: int = 1
    """Number of repetitions for this scan."""

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


class FastCyclicVoltammetry(
    BaseTechnique,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.IrDropCompensationMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create fast cyclic voltammetry method parameters.

    In Cyclic Voltammetry a cyclic potential scan is performed between two vertex potentials
    `vertex1_potential` and `vertex2_potential`.
    The scan can start (`begin_potential`) at one of these vertex potentials or anywhere in between.

    A CV becomes a Fast CV if the scan rate in combination with `step_potential` results in a rate of over 2500
    points / second (`scan_rate` / `step_potential` > 2500).
    """

    id: ClassVar[str] = 'fcv'

    current_range: AllowedCurrentRanges = '1uA'
    """Fixed current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts and stops at in V."""

    vertex1_potential: float = 0.5
    """First potential where direction reverses in V."""

    vertex2_potential: float = -0.5
    """Second potential where direction reverses. V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    scanrate: float = 1.0
    """Scan rate in V/s.

    The applicable range depends on the value of `step_potential`."""

    n_scans: int = 1
    """Number of repetitions for this scan."""

    n_avg_scans: int = 1
    """The number of scan repetitions for averaging.

    In case `n_scans` is set to a value > 1, each scan in the measurement is the result
    of an average of multiple scans, where the number of scans averaged is
    specified with this value."""

    n_equil_scans: int = 1
    """Number of equilibration scans.

    During these scans, no data is recorded."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast cyclic voltammetry settings."""

        psmethod.Ranging = PSFixedCurrentRange(cr_string_to_enum(self.current_range))
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
        self.current_range = cr_enum_to_string(psmethod.Ranging.StartCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.vertex1_potential = single_to_double(psmethod.Vtx1Potential)
        self.vertex2_potential = single_to_double(psmethod.Vtx2Potential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.scanrate = single_to_double(psmethod.Scanrate)
        self.n_scans = psmethod.nScans
        self.n_avg_scans = psmethod.nAvgScans
        self.n_equil_scans = psmethod.nEqScans


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
    """Create AC Voltammetry method parameters.

    In AC Voltammetry a potential scan is made with a superimposed sine wave which has a
    relatively small amplitude (normally 5 – 10 mV) and a frequency of 10 – 2000 Hz.

    The AC signal superimposed on the DC-potential results in an AC response (i ac rms). The
    resulting AC response is plotted against the potential.
    """

    id: ClassVar[str] = 'acv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts at in V."""

    end_potential: float = 0.5
    """Potential where the scan stops at in V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    ac_potential: float = 0.01
    """RMS amplitude of the applied sine wave in V."""

    frequency: float = 100.0
    """Frequency of the applied AC signal in HZ."""

    scanrate: float = 1.0
    """The applied scan rate in V/s

    The applicable range depends on the value of `step_potential`."""

    measure_dc_current: bool = False
    """Measure the DC current seperately.

    If True, the direct current (DC) will be measured separately
    and added to the measurement as an additional curve."""

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
    """Create linear sweep method parameters.

    In Linear Sweep Voltammetry a potential scan is performed from `begin_potential`,
    to `end_potential`. The scan is not exactly linear, but small potential steps (`potential_step`)
    are made.

    The current is sampled during the last 25% interval period of each step.
    The number of points in a curve showing the current versus potential is
    (`begin_potential` – `end_potential`) / (`step_potential` + 1).

    The scan rate is specified in V/s, which determines the time between two steps and thus the
    sampling time. The interval time is equal to `potential_step` / `scan_rate`.
    """

    id: ClassVar[str] = 'lsv'

    equilibration_time: float = 0.0
    """Equilibration time in s.

    Begin potential is applied during equilibration and the device switches to the appropriate current range."""

    begin_potential: float = -0.5
    """Potential where the scan starts at in V."""

    end_potential: float = 0.5
    """Potential where the scan stops at in V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    scanrate: float = 1.0
    """Scan rate in V/s.

    The applicable range depends on the value of `step_potential` since the data
    acquisition rate is limited by the connected instrument."""

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
    """Create square wave method parameters.

    Square wave Voltammetry (SWV) is in fact a special version of DPV.

    DPV is SWV when the pulse time is equal to the interval / 2. The interval time is the inverse of the
    frequency (1 / `frequency`). Like DPV, the pulse amplitude is also normally in the range of 5 - 25 or 50 mV.
    """

    id: ClassVar[str] = 'swv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts at in V."""

    end_potential: float = 0.5
    """Potential where the scan stops at in V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    frequency: float = 10.0
    """Frequency of the square wave in Hz."""

    amplitude: float = 0.05
    """Amplitude of square wave pulse in V.

    Values are defined as the half peak-to-peak value."""

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
    """Record forward and reverse currents."""

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
    """Create differential pulse voltammetry method parameters.

    In Differential Pulse Voltammetry a potential scan is made using pulses with a constant
    amplitude of `pulse_potential` superimposed on the dc-potential. The amplitude is mostly in the range
    of 5 – 50 mV.
    """

    id: ClassVar[str] = 'dpv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts at in V."""

    end_potential: float = 0.5
    """Potential where the scan stops at in V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    pulse_potential: float = 0.05
    """Pulse potential height in V."""

    pulse_time: float = 0.01
    """Pulse time in s.

    This duration needs to be set shorter than 0.5 * interval time
    where the interval time is equal to `potential_step` / `scan_rate`.
    """

    scan_rate: float = 1.0
    """Scan rate (potential/time) in V/s.

    The maximum scan rate depends on the value of `step_potential` step and `pulse_time`.
    The scan rate must be < (`step_potential` / `pulse_time`)."""

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
    """Create normal pulse voltammetry method parameters.

    In Normal Pulse Voltammetry (NPV) a potential scan is conducted in pulses by consistently
    increasing the pulse amplitude. The influence of diffusion
    limitation on your i-E curve (Cottrel behavior) is removed. NPV is normally more sensitive than
    LSV, since the diffusion layer thickness will be smaller, resulting in a higher faradaic current.
    """

    id: ClassVar[str] = 'npv'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts at in V."""

    end_potential: float = 0.5
    """Potential where the scan stops at in V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    pulse_time: float = 0.01
    """Pulse time in s.

    This duration needs to be set
    shorter than `0.5 * interval_time` where the interval time is equal to
    `potential_step` / `scan_rate`.
    """

    scan_rate: float = 1.0
    """The applied scan rate (potential/time) in V/s.

    The maximum scan rate depends on the value of `step_potential` step and `pulse_time`.
    The scan rate must be < (`step_potential` / `pulse_time`)."""

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
    """Create chrono amperometry method parameters.

    The instrument applies a constant DC-potential (E dc) and the current is measured
    with constant interval times.
    """

    id: ClassVar[str] = 'ad'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """Time between two current samples in s."""

    potential: float = 0.0
    """The potential applied during the measurement in V."""

    run_time: float = 1.0
    """Total run time of the measurement in s."""

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
    """Create fast amperometry method parameters.

    Fast amperometry is a form of Amperometric Detection (Chronoamperometry) but with very
    high sampling rates or very short interval times.
    """

    id: ClassVar[str] = 'fam'

    current_range: AllowedCurrentRanges = '100nA'
    """Fixed current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    equilibration_potential: float = 1.0
    """Equilibration potential at which the measurement starts in V."""

    interval_time: float = 0.1
    """Time between two current samples in s."""

    potential: float = 0.5
    """Potential during measurement in V.

    Note that this value is not relative to 'equilibration_potential`.
    The current is continuously sampled during this stage.
    """

    run_time: float = 1.0
    """Total run time of the measurement in s.

    Applicable run time: 1 ms to 30 s.
    """

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast amperometry settings."""
        psmethod.Ranging = PSFixedCurrentRange(cr_string_to_enum(self.current_range))
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.EqPotentialFA = self.equilibration_potential
        psmethod.IntervalTime = self.interval_time
        psmethod.Potential = self.potential
        psmethod.RunTime = self.run_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.current_range = cr_enum_to_string(psmethod.Ranging.StartCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.equilibration_potential = single_to_double(psmethod.EqPotentialFA)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.potential = single_to_double(psmethod.Potential)
        self.run_time = single_to_double(psmethod.RunTime)


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
    """Create multi-step amperometry method parameters.

    With Multistep amperometry you can specify the number of potential steps
    to apply and how long each step should last. Each step works exactly as a
    Chronoamperometry step. The current is continuously sampled with the specified interval
    time. A whole cycle of steps can be repeated several times.

    Levels can be specified using `pypalmsens.settings.ELevel`.
    """

    id: ClassVar[str] = 'ma'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    n_cycles: int = 1
    """Number of repetitions."""

    levels: list[ELevel] = Field(default_factory=lambda: [ELevel()])
    """The cto apply within a cycle.

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
    """Create pulsed amperometric detection method parameters.

    With Pulsed Amperometric Detection a series of pulses (pulse profile) is periodically repeated.
    Pulsed Amperometric Detection can be used when higher sensitivity is required. Using pulses
    instead of constant potential might result in higher faradaic currents. PAD is also used when the
    electrode surface has to be regenerated continuously, for instance, to remove adsorbents from
    the electrode surface.
    """

    id: ClassVar[str] = 'pad'

    _MODES: tuple[Literal['dc', 'pulse', 'differential'], ...] = ('dc', 'pulse', 'differential')

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    potential: float = 0.5
    """DC or base potential in V."""

    pulse_potential: float = 0.05
    """Pulse potential in V.

    Note that this value is not relative to `potential` given above."""

    pulse_time: float = 0.01
    """Pulse time in s."""

    mode: Literal['dc', 'pulse', 'differential'] = 'dc'
    """Measurement mode.

    - dc: measurement is performed at `potential`
    - pulse: measurement is performed at `pulse_potential`
    - differential: measurement is the difference (pulse - dc)
    """

    interval_time: float = 0.1
    """Time between two current samples in s."""

    run_time: float = 10.0
    """Total run time of the measurement in s.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (~278 hours).
    """

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


class MultiplePulseAmperometry(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
):
    """Create multiple pulse amperometry method parameters.

    The Multiple Pulse Amperometry (MPAD) technique involves applying a series of voltage pulses
    to an electrode immersed in a sample solution, and the resulting current of one of the pulses is
    measured.
    """

    id: ClassVar[str] = 'mpad'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    run_time: float = 10.0
    """Total run time of the measurement in s.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (~278 hours).
    """

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
    """Create open circuit potentiometry method parameters.

    For Open Circuit Potentiometry there is no polarization, and the so-called Open Circuit
    Potential (OCP) is measured and recorded with constant interval times. The result is a curve of
    Potential vs. Time. The OCP is also called Open Circuit Voltage (OCV).

    In corrosion, it is referred to as the "Corrosion Potential" (Ecorr), but in this context, it
    specifically denotes the potential of a metal or electrode when exposed to a corrosive
    environment.

    This method is the same as `Chronopotentiometry(current=0)`.
    """

    id: ClassVar[str] = 'ocp'

    interval_time: float = 0.1
    """Time between two potential samples in s."""

    run_time: float = 1.0
    """Total run time of the measurement in s.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (~278 hours).
    """

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record working electrode current."""

    record_we_current_range: AllowedCurrentRanges = '1uA'
    """Record working electrode current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with open circuit potentiometry settings."""
        psmethod.IntervalTime = self.interval_time
        psmethod.RunTime = self.run_time
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.record_we_current_range)

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.run_time = single_to_double(psmethod.RunTime)
        self.record_we_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


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
    """Create potentiometry method parameters.

    Chronopotentiometry (CP) is an electrochemical technique
    that requires a galvanostat instead of a potentiostat.
    In this method, a constant current is applied, and the resulting potential (voltage)
    is continuously recorded over time in a definite time interval. This technique is particularly
    useful for studying electrochemical reactions, kinetics, and processes under non-steady-state
    conditions, offering valuable insights into how the electrode potential evolves in response to
    the applied current.
    """

    id: ClassVar[str] = 'pot'

    current: float = 0.0
    """The current to apply in the given current range.

    Note that this value acts as a multiplier in the `applied_current_range`.

    So if 10 uA is the `applied_current_range` and 1.5 is given as current value,
    the applied current will be 15 uA."""

    applied_current_range: AllowedCurrentRanges = '100mA'
    """Applied current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    interval_time: float = 0.1
    """Time between two potential samples in s."""

    run_time: float = 1.0
    """Total run time of the measurement in s."""

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
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.IntervalTime = self.interval_time
        psmethod.RunTime = self.run_time

        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.current = single_to_double(psmethod.Current)
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.run_time = single_to_double(psmethod.RunTime)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


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

    Chronopotentiometric Stripping or Stripping chronopotentiometry is a sensitive analytical
    technique.
    The sequence of a stripping chronopotentiometry measurement:

    1. Apply conditioning potential, if conditioning time > 0.
    2. Apply deposition potential, if deposition time > 0.
    3. Apply deposition potential and wait for equilibration time.
    4. If the stripping current is set to 0 then the cell is switched off. Otherwise,
    the specified constant current is applied. The measurement with a rate of 40 kHz starts. The measurement
    stops when either the measured potential is below ‘end_potential’ or the `measurement_time` is exceeded.
    """

    id: ClassVar[str] = 'scp'

    potential_range: AllowedPotentialRanges = '500mV'
    """Fixed potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    current: float = 0.0
    """The stripping current to apply.

    Note that this value acts as a multiplier in the applied current range.
    So if 10 uA is the applied current range and 1.5 is given as current value,
    the applied current will be 15 uA.

    If the stripping current is set to 0, then chemical stripping is performed,
    otherwise it is chemical constant current stripping.
    """

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    end_potential: float = 0.0
    """Potential where the measurement at stops in V ."""

    measurement_time: float = 1.0
    """The maximum measurement time in s.

    This value should always exceed the required measurement time.
    It only limits the time of the measurement.
    When the potential response is erroneously and `end_potential` is not reached within this time,
    the measurement is aborted."""

    bandwidth: None | float = None
    """Override the bandwidth filter cutoff frequency (in Hz)."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with stripping chrono potentiometry settings."""
        psmethod.RangingPotential = PSFixedPotentialRange(
            pr_string_to_enum(self.potential_range)
        )

        psmethod.Istrip = self.current
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.MeasurementTime = self.measurement_time
        psmethod.EndPotential = self.end_potential

        if self.bandwidth is not None:
            psmethod.OverrideBandwidth = True
            psmethod.Bandwidth = self.bandwidth

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.potential_range = pr_enum_to_string(psmethod.RangingPotential.StartPotentialRange)

        self.current = single_to_double(psmethod.Current)
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.measurement_time = single_to_double(psmethod.MeasurementTime)
        self.end_potential = single_to_double(psmethod.EndPotential)

        if psmethod.OverrideBandwidth:
            self.bandwidth = single_to_double(psmethod.Bandwidth)


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

    id: ClassVar[str] = 'lsp'

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

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
    """Scan rate (current/time) in V/s.

    The applicable range depends on the value of `current_step` since the data
    acquisition rate is limited by the connected instrument.

    This value is multiplied by the defined current range."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record working electrode current."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with lineas sweep potentiometry settings."""
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)

        psmethod.BeginCurrent = self.current_begin
        psmethod.EndCurrent = self.current_end
        psmethod.StepCurrent = self.current_step
        psmethod.ScanrateG = self.scan_rate

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)

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
    """Create multi-step potentiometry method parameters.

    MultiStep Potentiometry you can specify the number of current steps
    to apply and how long each step should last. The current is continuously
    sampled with the specified interval.

    A whole cycle of steps can be repeated several times.

    Levels can be specified using `pypalmsens.settings.ILevel()`.
    """

    id: ClassVar[str] = 'mp'

    applied_current_range: AllowedCurrentRanges = '1uA'
    """Applied current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    n_cycles: int = 1
    """Number of repetitions."""

    levels: list[ILevel] = Field(default_factory=lambda: [ILevel()])
    """The currents to apply within a cycle.

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
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
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
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)

        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.n_cycles = psmethod.nCycles

        self.levels = [ILevel.from_psobj(pslevel) for pslevel in psmethod.Levels]

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


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
    """Create chrono coulometry method parameters.

    Chronoamperometry (CA) and Chronocoulometry (CC) have the same potential waveform but
    in CC, the charge is monitored as a function of time (instead of the current).
    The charge is determined by integrating the current.
    """

    id: ClassVar[str] = 'cc'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    step1_potential: float = 0.5
    """Potential applied during first step in V."""

    step1_run_time: float = 5.0
    """Run time for the first step.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (ca. 278 hours).
    """

    step2_potential: float = 0.5
    """Potential applied during second step in V."""

    step2_run_time: float = 5.0
    """Run time for the second step.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (ca. 278 hours).
    """

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
    """Create potentiometry method parameters.

    Electrochemical Impedance Spectroscopy (EIS) is an electrochemical technique to measure
    the impedance of a system in dependence of the AC potentials frequency.

    Although "spectroscopy" implies a frequency sweep, which is the most common
    measurement, this class provide the flexibility to set the frequency and vary
    other parameters, such as DC potential and time.

    Available modes of EIS measurements:

    - a frequency scan at a fixed dc-potential (default EIS)
    - frequency scans at each dc-potential in a potential scan
    - frequency scans at specified time intervals (time scan)
    - a single frequency applied at each dc potential in a potential scan (Mott-Schottky)
    - a repeated single frequency at specified time intervals
    """

    id: ClassVar[str] = 'eis'

    _SCAN_TYPES: tuple[Literal['potential', 'time', 'fixed'], ...] = (
        'potential',
        'time',
        'fixed',
    )
    _FREQ_TYPES: tuple[Literal['fixed', 'scan'], ...] = ('fixed', 'scan')

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    dc_potential: float = 0.0
    """DC-potential applied during the EIS scan in V.

    Also called _DC Bias_ or _level_.
    The most common setting for this parameter is 0 V vs. OCP."""

    ac_potential: float = 0.01
    """AC potential in V RMS.

    The amplitude of the ac potential signal has a range of 0.001 V to 0.25 V
    (RMS). In many applications, a value of 0.010 V (RMS) is used.
    """

    frequency_type: Literal['fixed', 'scan'] = 'scan'
    """Whether to measure a single frequency or scan over a range of frequencies.

    Possible values: 'scan', 'fixed'.

    - Scan: a frequency scan is performed starting at the given `max_frequency`
        to the `min_frequency`.
    - Fixed: a single frequency given by 'fixed_frequencya is applied for
        the given duration or at each potential step or time interval.
    """

    fixed_frequency: float = 1_000
    """Fixed frequency in Hz (fixed frequency only)."""

    min_frequency: float = 5.0
    """Minimum frequency in Hz (frequency scan only)."""

    max_frequency: float = 10_000
    """Maximum frequency in Hz (frequency scan only)."""

    n_frequencies: int = 11
    """Number of frequencies (frequency scan only).

    Defines the range of frequencies to apply between the `max_frequency` and
    `min_frequency`. For example, a value of 11 will measure at 11 frequencies,
    including both end points.
    """

    scan_type: Literal['potential', 'time', 'fixed'] = 'fixed'
    """Whether a single or multiple frequency scans are performed.

    Possible values: 'potential', 'time', 'fixed'.

    - Fixed scan: perform a single scan (default).
    - Time scan: scans are repeated for a specific amount of time at a specific interval.
    - Potential scan: scans are repeated over a range of DC potential values.
      A potential scan should not be performed versus the OCP.
    """

    run_time: float = 10.0
    """Minimal run time in seconds (time scan only).

    For example, if a frequency scan takes 18 seconds and is measured
    at an interval of 19 seconds for a `run_time` of 40 seconds, then
    three iterations will be performed."""

    interval_time: float = 0.1
    """The interval at which a measurement iteration should be performed (time scan only).

    The minimum interval time between each data point (`frequency_type='fixed') or
    between each frequency scan (`frequency_type='scan').
    We recommend a time higher than the required time to measure the data point or perform the
    frequency scan + overhead time. While it's possible to use a shorter time, doing so may
    lead to incorrect impedance calculations.

    If a measurement iteration takes longer than the interval time the next measurement
    will not be triggered until after it has been completed.
    """

    begin_potential: float = 0.0
    """The dc-potential at which the measurement starts in V (potential scan only).

    I.e. the DC potential of the applied sine wave to start the series of iterative measurements at.
    """

    end_potential: float = 0.0
    """The dc-potential at which the scan ends in  V (potential scan only).

    I.e. the DC potential of the applied sine wave at which the series of iterative measurements ends.
    """

    step_potential: float = 0.01
    """Potential step size in V (potential scan only).

    This sets the increment to be used between `begin_potential` and `end_potential`.
    """

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

        psmethod.FixedFrequency = self.fixed_frequency
        psmethod.MaxFrequency = self.max_frequency
        psmethod.MinFrequency = self.min_frequency

        psmethod.nFrequencies = self.n_frequencies
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

        self.fixed_frequency = single_to_double(psmethod.FixedFrequency)
        self.max_frequency = single_to_double(psmethod.MaxFrequency)
        self.min_frequency = single_to_double(psmethod.MinFrequency)

        if self.scan_type == 'potential':
            self.begin_potential = single_to_double(psmethod.BeginPotential)
            self.end_potential = single_to_double(psmethod.EndPotential)
            self.step_potential = single_to_double(psmethod.StepPotential)
        elif self.scan_type == 'time':
            self.run_time = single_to_double(psmethod.RunTime)
            self.interval_time = single_to_double(psmethod.IntervalTime)


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

    id: ClassVar[str] = 'fis'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    run_time: float = 10.0
    """Total run time of the measurement in s."""

    dc_potential: float = 0.0
    """Potential applied during measurement in V."""

    ac_potential: float = 0.01
    """Potential amplitude in V (rms)."""

    frequency: float = 50000.0
    """Fixed frequency in Hz."""

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
    """Create galvanostatic impedance spectroscopy method parameters.

    For Galvanostatic EIS (GEIS) the modes are:

    - a frequency scan at a fixed dc-current
    - frequency scans at each current in a current scan
    - frequency scans at specified time intervals (time scan)
    - a single frequency applied at each current in a current scan
    - a single frequency at specified time intervals
    """

    id: ClassVar[str] = 'gis'

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    ac_current: float = 0.01
    """AC current in applied current range RMS."""

    dc_current: float = 0.0
    """DC current in applied current range."""

    min_frequency: float = 1_000
    """Minimum frequency in Hz."""

    max_frequency: float = 50_000
    """Maximum frequency in Hz."""

    n_frequencies: int = 11
    """Number of frequencies."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with galvanic impedance spectroscopy settings."""

        psmethod.ScanType = enumScanType.Fixed
        psmethod.FreqType = enumFrequencyType.Scan
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.Iac = self.ac_current
        psmethod.Idc = self.dc_current
        psmethod.nFrequencies = self.n_frequencies
        psmethod.MaxFrequency = self.max_frequency
        psmethod.MinFrequency = self.min_frequency

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.ac_current = single_to_double(psmethod.Iac)
        self.dc_current = single_to_double(psmethod.Idc)
        self.n_frequencies = psmethod.nFrequencies
        self.max_frequency = single_to_double(psmethod.MaxFrequency)
        self.min_frequency = single_to_double(psmethod.MinFrequency)


class FastGalvanostaticImpedanceSpectroscopy(
    BaseTechnique,
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.GeneralMixin,
):
    """Create fast galvanostatic impededance spectroscopy method parameters."""

    id: ClassVar[str] = 'fgis'

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    run_time: float = 10.0
    """Total run time of the measurement in s."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    ac_current: float = 0.01
    """AC current in applied current range RMS.

    This value is multiplied by the applied current range."""

    dc_current: float = 0.0
    """DC current in applied current range.

    This value is multiplied by the applied current range."""

    frequency: float = 50000.0
    """Fixed frequency in Hz."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        """Update method with fast galvanic impedance spectroscopy settings."""
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.Iac = self.ac_current
        psmethod.Idc = self.dc_current
        psmethod.FixedFrequency = self.frequency
        psmethod.RunTime = self.run_time
        psmethod.IntervalTime = self.interval_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.ac_current = single_to_double(psmethod.Iac)
        self.dc_current = single_to_double(psmethod.Idc)
        self.frequency = single_to_double(psmethod.FixedFrequency)
        self.run_time = single_to_double(psmethod.RunTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)


class MethodScript(BaseTechnique):
    """Create a method script sandbox object.

    The MethodSCRIPT Sandbox allows you to write your own MethodSCRIPT and run them
    on your instrument.

    The MethodSCRIPT language allows for programming a human-readable script directly into the
    potentiostat. The simple script language makes it easy to combine different measurements and
    other tasks.

    For more information see:
        https://www.palmsens.com/methodscript/
    """

    id: ClassVar[str] = 'ms'

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
