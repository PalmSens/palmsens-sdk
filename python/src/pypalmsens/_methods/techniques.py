from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from typing import Literal

import PalmSens
from PalmSens import Techniques as PSTechniques
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType
from pydantic import Field, field_validator, model_validator
from typing_extensions import Self, override

from .._converters import (
    cr_enum_to_string,
    cr_string_to_enum,
    pr_enum_to_string,
    pr_string_to_enum,
    single_to_double,
)
from .._methodscript import validate as validate_methodscript
from .._types import (
    AllowedCurrentRanges,
    AllowedFrequencyTypes,
    AllowedPotentialRanges,
    AllowedScanTypes,
)
from . import mixins
from .base import BaseTechnique, LablinkParameters
from .levels import (
    ELevel,
    ILevel,
)
from .mask import (
    get_extra_value_mask,
    set_extra_value_mask,
)
from .settings import CustomUnits


class BaseCyclicVoltammetry(
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
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Cyclic voltammetry parameters shared by the CV techniques."""

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
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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


class CyclicVoltammetry(BaseCyclicVoltammetry):
    """Create cyclic voltammetry method parameters.

    In Cyclic Voltammetry, repeated potential scans are performed between
    `vertex1_potential` and `vertex2_potential`, with the number of scans
    determined by `n_scans`. The scan starts at `begin_potential`, which can be
    one of these vertex potentials or any value in between, and the experiment
    always terminates at the same potential as `begin_potential`.

    The scan is not linear but a staircase of `step_potential` steps, and the
    current is sampled during the last quarter of each step. This gives an
    interval time of `step_potential / scanrate` between two points, and each
    scan covers the potential window twice.

    A `current_limits` value reverses the scan direction before the next vertex
    is reached, protecting the working electrode when the potential that causes
    an excessive current is not known in advance.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.CyclicVoltammetry(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     vertex1_potential=0.5,
    ...     vertex2_potential=-0.5,
    ...     step_potential=0.1,
    ...     scanrate=1.0,
    ...     n_scans=1,
    ... )
    """

    id: Literal['cv'] = 'cv'
    """Unique method identifier."""


class FastCyclicVoltammetry(
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.IrDropCompensationMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create fast cyclic voltammetry method parameters.

    In Cyclic Voltammetry, a cyclic potential scan is performed between the two
    vertex potentials `vertex1_potential` and `vertex2_potential`. The scan can
    start at `begin_potential`, which may be either vertex or any value in
    between.

    Use Fast CV when `scanrate` and `step_potential` imply a sampling
    rate above 2500 points/s (`scanrate / step_potential > 2500`).

    Auto-ranging is impossible at these speeds, so `current_range` is a single
    fixed range. Averaging scans with `n_avg_scans` and discarding
    `n_equil_scans` scans before recording can reduce noise, but removing the
    noise at its source is preferable.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.FastCyclicVoltammetry(
    ...     current_range='1uA',
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     vertex1_potential=0.5,
    ...     vertex2_potential=-0.5,
    ...     step_potential=0.1,
    ...     scanrate=1.0,
    ...     n_scans=1,
    ...     n_avg_scans=1,
    ...     n_equil_scans=1,
    ... )
    """

    id: Literal['fcv'] = 'fcv'
    """Unique method identifier."""

    current_range: AllowedCurrentRanges = '1uA'
    """Fixed current range."""

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
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with fast cyclic voltammetry settings."""

        psmethod.Ranging = PalmSens.FixedCurrentRange(cr_string_to_enum(self.current_range))
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
    def _import(self, psmethod: PalmSens.Method, /):
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
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create AC Voltammetry method parameters.

    In AC Voltammetry a potential scan is made with a superimposed sine wave which has a
    relatively small amplitude (normally 5 – 10 mV) and a frequency of 10 – 2000 Hz.

    The AC signal superimposed on the DC-potential results in an AC response (i ac rms). The
    resulting AC response is plotted against the potential.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.ACVoltammetry(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     ac_potential=0.01,
    ...     frequency=100.0,
    ...     scanrate=1.0,
    ...     measure_dc_current=False,
    ... )
    """

    id: Literal['acv'] = 'acv'
    """Unique method identifier."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    begin_potential: float = -0.5
    """Potential where the scan starts at in V."""

    end_potential: float = 0.5
    """Potential where the scan stops at in V."""

    step_potential: float = 0.1
    """Potential step size in V."""

    ac_potential: float = 0.01
    """RMS amplitude of the applied sine wave in V.

    Normally 5-10 mV."""

    frequency: float = 100.0
    """Frequency of the applied AC signal in Hz."""

    scanrate: float = 1.0
    """The applied scan rate in V/s

    The applicable range depends on the value of `step_potential`."""

    measure_dc_current: bool = False
    """Measure the DC current separately.

    If True, the direct current (DC) will be measured separately
    and added to the measurement as an additional curve."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.begin_potential = single_to_double(psmethod.BeginPotential)
        self.end_potential = single_to_double(psmethod.EndPotential)
        self.step_potential = single_to_double(psmethod.StepPotential)
        self.ac_potential = single_to_double(psmethod.SineWaveAmplitude)
        self.frequency = single_to_double(psmethod.Frequency)
        self.scanrate = single_to_double(psmethod.Scanrate)
        self.measure_dc_current = psmethod.MeasureDCcurrent


class BaseLinearSweepVoltammetry(
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
    BaseTechnique,
):
    """Linear sweep parameters shared by the scan-based voltammetry techniques."""

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
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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


class LinearSweepVoltammetry(BaseLinearSweepVoltammetry):
    """Create linear sweep method parameters.

    In Linear Sweep Voltammetry, a potential scan is performed from
    `begin_potential` to `end_potential`. The scan is a staircase of
    `step_potential` steps rather than a true ramp.

    The current is sampled during the last quarter of each step, so the
    interval time is `step_potential / scanrate`. The number of points in a
    curve showing the current versus potential is
    (`end_potential` - `begin_potential`) / `step_potential` + 1.

    The scan rate is specified in V/s and determines the time between two steps,
    and therefore the sampling time. A larger `step_potential` collects data
    faster and can improve the signal-to-noise ratio; a smaller one gives better
    resolution and sensitivity. For scan rates of 0.01 to 0.1 V/s, steps of 3 to
    10 mV are a sensible starting point.

    A `current_limits` value stops the scan before `end_potential` is reached,
    which protects the working electrode when the potential that causes an
    excessively high current is not known in advance.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.LinearSweepVoltammetry(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     scanrate=1.0,
    ... )
    """

    id: Literal['lsv'] = 'lsv'
    """Unique method identifier."""


class SquareWaveVoltammetry(
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
    BaseTechnique,
):
    """Create square wave method parameters.

    Square wave voltammetry (SWV) is closely related to differential pulse voltammetry (DPV).
    DPV becomes SWV when the pulse time is half the interval time. The interval time is the inverse of the
    frequency (1 / `frequency`). As in DPV, the pulse amplitude is normally 5 - 25 or 50 mV.

    Plotting the forward and reverse currents side by side
    (`record_forward_and_reverse_currents`) shows how reversible, i.e. how fast,
    the electrode reaction is.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.SquareWaveVoltammetry(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     frequency=10.0,
    ...     amplitude=0.05,
    ... )
    """

    id: Literal['swv'] = 'swv'
    """Unique method identifier."""

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
    """Record forward and reverse currents.

    Adds a separate curve for the current measured during the positive and the
    negative pulse. Not supported by PalmSens1 and PalmSens2."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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
    BaseTechnique,
):
    """Create differential pulse voltammetry method parameters.

    In Differential Pulse Voltammetry, a potential scan is made using pulses of constant
    amplitude (`pulse_potential`) superimposed on the DC potential. The amplitude is typically
    5–50 mV.

    The current is sampled twice per step: just before the pulse is applied and at
    the end of it. The difference between these two samples is plotted against the
    potential, producing a peak-shaped curve proportional to the derivative of an LSV
    or NPV curve. Its peak height is normally proportional to the concentration.

    Note that the peak potential is not the redox potential:
    `E_peak = E_1/2 - pulse_potential / 2`.

    As in NPV, a longer `pulse_time` expands the diffusion layer and lowers the
    current, while a shorter `pulse_time` increases the capacitive current and therefore
    the (non-linear) baseline. For trace analysis, the optimal pulse time is found
    empirically by varying `pulse_time`.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.DifferentialPulseVoltammetry(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     pulse_potential=0.05,
    ...     pulse_time=0.01,
    ...     scan_rate=1.0,
    ... )
    """

    id: Literal['dpv'] = 'dpv'
    """Unique method identifier."""

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
    where the interval time is equal to `step_potential` / `scan_rate`.
    """

    scan_rate: float = 1.0
    """Scan rate (potential/time) in V/s.

    The maximum scan rate depends on the value of `step_potential` and `pulse_time`.
    The scan rate must be < (`step_potential` / 2 * `pulse_time`)."""

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
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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
    BaseTechnique,
):
    """Create normal pulse voltammetry method parameters.

    In Normal Pulse Voltammetry (NPV) a potential scan is conducted in pulses by consistently
    increasing the pulse amplitude. The influence of diffusion
    limitation on your i-E curve (Cottrel behavior) is removed. NPV is normally more sensitive than
    LSV, since the diffusion layer thickness will be smaller, resulting in a higher faradaic current.

    The pulse grows with the scan: it equals `step_potential` at the first step,
    twice that at the next, and so on until `begin_potential` + n * `step_potential`
    reaches `end_potential`, with n = (`end_potential` - `begin_potential`) /
    `step_potential`.

    A longer `pulse_time` grows the diffusion layer and lowers the sampled
    current; a short pulse increases the capacitive current and therefore the
    (non-linear) baseline.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.NormalPulseVoltammetry(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     pulse_time=0.01,
    ...     scan_rate=1.0,
    ... )
    """

    id: Literal['npv'] = 'npv'
    """Unique method identifier."""

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
    `step_potential` / `scan_rate`.
    """

    scan_rate: float = 1.0
    """The applied scan rate (potential/time) in V/s.

    The maximum scan rate depends on the value of `step_potential` and `pulse_time`.
    The scan rate must be < (`step_potential` / 2 * `pulse_time`)."""

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
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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


class BaseChronoAmperometry(
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
    BaseTechnique,
    mixins.GeneralMixin,
):
    equilibration_time: float = 0.0
    """Equilibration time in s.

    If not zero, the potential is applied and held for this long before the
    measurement starts. No data are recorded during the equilibration step."""

    interval_time: float = 0.1
    """Time between two current samples in s."""

    potential: float = 0.0
    """The potential applied during the measurement in V.

    Must be within the applicable potential range of the instrument. It is
    irrelevant in a zero resistance amperometry setup, where the reference and
    counter electrodes are not part of the measured circuit."""

    run_time: float = 1.0
    """Total run time of the measurement in s.

    Between 5 * `interval_time` and 1,000,000 seconds (ca. 278 hours)."""

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
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _lablink_export(self, parameters: LablinkParameters, /):
        """Update lablink parameters with chrono amperometry settings."""
        parameters['EquilibrationTime'] = [self.equilibration_time]
        parameters['IntervalTime'] = [self.interval_time]
        parameters['Potential'] = [self.potential]
        parameters['RunTime'] = [self.run_time]

        parameters['MeasureAuxiliaryInput'] = [self.record_auxiliary_input]
        parameters['MeasureCellPotential'] = [self.record_cell_potential]
        parameters['MeasureWEPotential'] = [self.record_we_potential]

        if self.enable_bipot_current:
            # used in combination with bipot mixin
            raise NotImplementedError

    @override
    def _import(self, psmethod: PalmSens.Method, /):
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


class ChronoAmperometry(BaseChronoAmperometry):
    """Create chrono amperometry method parameters.

    Also known as Amperometric Detection or Potentiostatic Step.
    The instrument applies a constant DC potential (`potential`) and
    the current is measured at constant `interval_time` intervals.
    If `equilibration_time` is not zero, the potential is applied
    first and held without recording data.

    Chronoamperometry is also the way to record zero resistance amperometry
    (ZRA) and electrochemical noise: the potentiostat then works as an ammeter,
    `potential` is irrelevant, and `record_we_potential` adds the working
    electrode versus reference electrode potential to the record. Such a setup
    needs a floating (galvanically isolated) instrument and the cell cannot be
    disconnected on overload, so keep the current within the specifications of
    the instrument.

    If you need to run faster steps, use
    [FastAmperometry][pypalmsens.FastAmperometry] instead.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.ChronoAmperometry(
    ...     equilibration_time=0.0,
    ...     interval_time=0.1,
    ...     potential=0.0,
    ...     run_time=1.0,
    ... )
    """

    id: Literal['ad'] = 'ad'
    """Unique method identifier."""


class FastAmperometry(
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
    BaseTechnique,
):
    """Create fast amperometry method parameters.

    Use Fast amperometry if you need Amperometric Detection (Chronoamperometry)
    with very high sampling rates or very short interval times.

    Only the Nexus, PalmSens and EmStat4 LR/HR series support this technique.
    The current range is fixed for the whole measurement, and the potential of
    the pulse (`potential`) is applied after the equilibration step, which runs
    at its own `equilibration_potential`.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.FastAmperometry(
    ...     current_range='100nA',
    ...     equilibration_time=0.0,
    ...     equilibration_potential=1.0,
    ...     interval_time=0.1,
    ...     potential=0.5,
    ...     run_time=1.0,
    ... )
    """

    id: Literal['fam'] = 'fam'
    """Unique method identifier."""

    current_range: AllowedCurrentRanges = '100nA'
    """Fixed current range.

    Unlike most techniques, fast amperometry does not auto-range: the current
    stays in this range for the entire measurement."""

    equilibration_time: float = 0.0
    """Equilibration time in s.

    `equilibration_potential` is applied during this step, without recording
    data."""

    equilibration_potential: float = 1.0
    """Equilibration potential at which the measurement starts in V."""

    interval_time: float = 0.1
    """Time between two current samples in s.

    Much shorter interval times are available than for chrono amperometry: the
    minimum is 0.25 ms for PalmSens 1 and 2, 0.01 ms for PalmSens 3, 0.02 ms
    for PalmSens 4 and 0.001 ms for EmStat4."""

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
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with fast amperometry settings."""
        psmethod.Ranging = PalmSens.FixedCurrentRange(cr_string_to_enum(self.current_range))
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.EqPotentialFA = self.equilibration_potential
        psmethod.IntervalTime = self.interval_time
        psmethod.Potential = self.potential
        psmethod.RunTime = self.run_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.current_range = cr_enum_to_string(psmethod.Ranging.StartCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.equilibration_potential = single_to_double(psmethod.EqPotentialFA)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.potential = single_to_double(psmethod.Potential)
        self.run_time = single_to_double(psmethod.RunTime)


class MultiStepAmperometry(
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.BiPotMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.IrDropCompensationMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create multi-step amperometry method parameters.

    With Multistep amperometry you can specify the number of potential steps
    to apply and how long each step should last. Each step works exactly as a
    Chronoamperometry step. The current is continuously sampled with the
    specified interval time. A whole cycle of steps can be repeated several times.

    Levels can be specified using [pypalmsens.settings.ELevel][]. Switching
    between levels adds overhead time, which is set out in
    [pypalmsens.settings.ELevel][] per instrument.

    Amperometric results are commonly analysed with a Cottrell plot, i.e. the
    current plotted against the inverse square root of time. Methods that need
    more complex behaviour than a fixed list of levels can be written as
    [MethodScript][pypalmsens.MethodScript] instead.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import ELevel
    >>> method = ps.MultiStepAmperometry(
    ...     equilibration_time=0.0,
    ...     interval_time=0.1,
    ...     n_cycles=1,
    ...     levels=[
    ...         ELevel(level=0.0, duration=1.0, record=True),
    ...     ],
    ... )
    """

    id: Literal['ma'] = 'ma'
    """Unique method identifier."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    n_cycles: int = 1
    """Number of repetitions."""

    levels: list[ELevel] = Field(default_factory=lambda: [ELevel()])
    """The potentials to apply within a cycle.

    The levels are applied one after another. Use `ELevel()` to create levels.
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
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with multistep amperometry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.IntervalTime = self.interval_time
        psmethod.nCycles = self.n_cycles
        psmethod.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            psmethod.Levels.Add(level._to_psobj())

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
    def _import(self, psmethod: PalmSens.Method, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.n_cycles = psmethod.nCycles

        self.levels = [ELevel._from_psobj(pslevel) for pslevel in psmethod.Levels]

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


class PulsedAmperometricDetection(
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
    BaseTechnique,
):
    """Create pulsed amperometric detection method parameters.

    In Pulsed Amperometric Detection, a pulse profile is periodically repeated.

    Each pulse applies `pulse_potential` for `pulse_time` on top of the base
    potential `potential`, which is held between pulses.

    Pulsed Amperometric Detection can be used when higher sensitivity is required. Applying
    pulses instead of a constant potential may produce higher faradaic currents. PAD is also
    used when the electrode surface must be regenerated continuously, for example to remove
    adsorbents from the electrode surface.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.PulsedAmperometricDetection(
    ...     equilibration_time=0.0,
    ...     potential=0.5,
    ...     pulse_potential=0.05,
    ...     pulse_time=0.01,
    ...     mode='dc',
    ...     interval_time=0.1,
    ...     run_time=10.0,
    ... )
    """

    id: Literal['pad'] = 'pad'
    """Unique method identifier."""

    _MODES: tuple[Literal['dc', 'pulse', 'differential'], ...] = ('dc', 'pulse', 'differential')

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    potential: float = 0.5
    """DC or base potential in V.

    Must be within the applicable potential range of the instrument."""

    pulse_potential: float = 0.05
    """Pulse potential in V.

    Note that this value is not relative to `potential` given above. It must be
    within the applicable pulse potential range of the instrument."""

    pulse_time: float = 0.01
    """Pulse time in s.

    The applicable pulse time range is instrument dependent: 10 ms to 1 s for
    PalmSens 1 and 2, 0.2 ms to 1 s for PalmSens 3, 0.4 ms to 1 s for PalmSens
    4 and Nexus, 5 ms to 1 s for EmStat 1, 2 and 3(+), 0.4 ms to 0.3 s for
    EmStat4, and 2 ms to 0.3 s for EmStat Pico."""

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
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.potential = single_to_double(psmethod.Potential)
        self.pulse_potential = single_to_double(psmethod.PulsePotentialAD)
        self.pulse_time = single_to_double(psmethod.PulseTime)
        self.run_time = single_to_double(psmethod.RunTime)

        self.mode = self._MODES[int(psmethod.tMode) - 1]


class MultiplePulseAmperometry(
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create multiple pulse amperometry method parameters.

    Multiple Pulse Amperometry (MPAD) applies a series of voltage pulses to an
    electrode immersed in a sample solution, and the current is measured during
    one of the pulses: `potential_1` is the level at which the current is
    recorded, while `potential_2` and `potential_3` shape the rest of the pulse
    profile.

    MPAD is used when higher sensitivity is required. Using pulses instead of a
    constant potential can produce higher faradaic currents, and because the
    electrode surface is regenerated with every pulse, adsorbents are removed
    continuously. This also reduces background noise and interference, making
    it useful for trace-level analytes in complex sample matrices. The
    potential levels and pulse durations can be optimised for each analyte,
    which is why MPAD is a common detector in liquid chromatography (HPLC),
    capillary electrophoresis, and flow injection analysis.

    Only the PalmSens series and EmStat 1, 2, and 3(+) support this technique.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.MultiplePulseAmperometry(
    ...     equilibration_time=0.0,
    ...     run_time=10.0,
    ...     duration_1=0.1,
    ...     duration_2=0.1,
    ...     duration_3=0.1,
    ...     potential_1=0.2,
    ...     potential_2=0.4,
    ...     potential_3=0.6,
    ... )
    """

    id: Literal['mpad'] = 'mpad'
    """Unique method identifier."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    run_time: float = 10.0
    """Total run time of the measurement in s.

    At least 5 times the sampling interval and at most 1,000,000 seconds
    (~278 hours). One pulse cycle takes
    `duration_1` + `duration_2` + `duration_3` seconds.
    """

    duration_1: float = 0.1
    """Duration of the first applied potential in s. Between 0.1 and 2 s."""

    duration_2: float = 0.1
    """Duration of the second applied potential in s. Between 0.1 and 2 s."""

    duration_3: float = 0.1
    """Duration of the third applied potential in s. Between 0.1 and 2 s."""

    potential_1: float = 0.0
    """First applied potential level at which the current is recorded in V.

    Must be within the applicable potential range of the instrument.
    """

    potential_2: float = 0.0
    """Second applied potential level at which the current is recorded in V."""

    potential_3: float = 0.0
    """Third applied potential level at which the current is recorded in V."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with multiple pulse amperometry settings."""
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.RunTime = self.run_time

        psmethod.E1 = self.potential_1
        psmethod.E2 = self.potential_2
        psmethod.E3 = self.potential_3
        psmethod.t1 = self.duration_1
        psmethod.t2 = self.duration_2
        psmethod.t3 = self.duration_3

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.run_time = single_to_double(psmethod.RunTime)

        self.potential_1 = single_to_double(psmethod.E1)
        self.potential_2 = single_to_double(psmethod.E2)
        self.potential_3 = single_to_double(psmethod.E3)
        self.duration_1 = single_to_double(psmethod.t1)
        self.duration_2 = single_to_double(psmethod.t2)
        self.duration_3 = single_to_double(psmethod.t3)


class BaseOpenCircuitPotentiometry(
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
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
    """Record the working electrode current.

    The current is measured in `record_we_current_range`. Recording the WE
    current is supported by PalmSens4 and EmStat4."""

    record_we_current_range: AllowedCurrentRanges = '1uA'
    """Current range used to record the working electrode current.

    OCP polarizes the cell with neither potential nor current, so the recording
    range is set here rather than through an applied current range.
    """

    @override
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.run_time = single_to_double(psmethod.RunTime)
        self.record_we_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


class OpenCircuitPotentiometry(BaseOpenCircuitPotentiometry):
    """Create open circuit potentiometry method parameters.

    Supported by all instruments.

    For Open Circuit Potentiometry there is no polarization, and the so-called Open Circuit
    Potential (OCP) is measured and recorded with constant interval times. The result is a curve of
    Potential vs. Time. The OCP is also called Open Circuit Voltage (OCV).

    In corrosion, it is referred to as the "Corrosion Potential" (Ecorr), but in this context, it
    specifically denotes the potential of a metal or electrode when exposed to a corrosive
    environment.

    This method is the same as [ChronoPotentiometry][pypalmsens.ChronoPotentiometry] with
    `current=0`.

    Examples
    --------
    Record OCP including working electrode current:

    >>> import pypalmsens as ps
    >>> method = ps.OpenCircuitPotentiometry(
    ...     interval_time=0.1,
    ...     run_time=1.0,
    ...     record_we_current=True,
    ...     record_we_current_range='1uA',
    ... )
    """

    id: Literal['ocp'] = 'ocp'
    """Unique method identifier."""


class BaseChronoPotentiometry(
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    current: float = 0.0
    """The current to apply in the given current range.

    Note that this value acts as a multiplier in the `applied_current_range`.

    So if 10 µA is the `applied_current_range` and 1.5 is given as current value,
    the applied current will be 15 µA.

    The largest usable multiplier is instrument dependent: ±2 times the range for
    PalmSens2, ±3 for PalmSens3, ±6 for PalmSens4, -3 to +3 for EmStat4 LR and HR,
    and on Nexus ±5 below 10 mA, ±4.5 for the 10 and 100 mA ranges and ±1 for the
    1 A range. The multiplier your instrument allows is available as `min_current`
    and `max_current` on [pypalmsens.InstrumentManager.capabilities][]."""

    applied_current_range: AllowedCurrentRanges = '100mA'
    """Applied current range."""

    interval_time: float = 0.1
    """Time between two potential samples in s."""

    run_time: float = 1.0
    """Total run time of the measurement in s.

    Between 5 * `interval_time` and 1,000,000 seconds (ca. 278 hours)."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_current: bool = False
    """Record working electrode current."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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


class ChronoPotentiometry(BaseChronoPotentiometry):
    """Create potentiometry method parameters.

    Also known as Galvanostatic Step. Supported by the Nexus series, the PalmSens
    series and EmStat4 LR and HR.

    Chronopotentiometry (CP) is an electrochemical technique
    that requires a galvanostat instead of a potentiostat.
    In this method, a constant current is applied, and the resulting potential (voltage)
    is continuously recorded over time in a definite time interval. This technique is particularly
    useful for studying electrochemical reactions, kinetics, and processes under non-steady-state
    conditions, offering valuable insights into how the electrode potential evolves in response to
    the applied current.

    CP is valuable when no reference electrode is available: the applied current
    stays constant even as the cell resistance changes.
    Combined with a known electrode surface area it gives a
    reproducible basis for quantitative work, such as determining reaction rate
    constants and charge transfer coefficients.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.ChronoPotentiometry(
    ...     current=0.0,
    ...     applied_current_range='100mA',
    ...     interval_time=0.1,
    ...     run_time=1.0,
    ... )
    """

    id: Literal['pot'] = 'pot'
    """Unique method identifier."""


class StrippingChronoPotentiometry(
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create stripping potentiometry method parameters.

    Also known as Potentiometric Stripping Analysis (PSA).

    Chronopotentiometric Stripping or Stripping chronopotentiometry is a sensitive analytical
    technique. The sequence of a stripping chronopotentiometry measurement:

    1. Apply conditioning potential, if conditioning time > 0.
    2. Apply deposition potential, if deposition time > 0.
    3. Apply deposition potential and wait for equilibration time.
    4. If the stripping current is set to 0 then the cell is switched off. Otherwise,
    the specified constant current is applied. The measurement with a rate of 40 kHz starts. The measurement
    stops when either the measured potential is below `end_potential` or the `measurement_time` is exceeded.

    The conditioning and deposition potentials of steps 1 and 2, with their times,
    come from [pypalmsens.settings.Pretreatment][]. During step 3 the deposition
    potential is held while the cell equilibrates.

    The measurement runs in one of two modes: chemical stripping, where a chemical
    oxidant or reductant strips the deposit, or galvanostatic stripping, where
    `current` is applied. Both record the potential versus time, and the result is
    conventionally re-plotted as the inverse derivative dt/dE in s/V against the
    potential. Stripping a deposit takes charge, so the more of a component was
    deposited, the longer it takes for the potential to move and the larger the
    peak in dt/dE at the potential where that component is oxidised or reduced.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.StrippingChronoPotentiometry(
    ...     potential_range='500mV',
    ...     current=0.0,
    ...     applied_current_range='100uA',
    ...     end_potential=0.0,
    ...     measurement_time=1.0,
    ... )
    """

    id: Literal['scp'] = 'scp'
    """Unique method identifier."""

    potential_range: AllowedPotentialRanges = '500mV'
    """Potential range used for the whole measurement.

    Unlike other techniques, this range is fixed: it is not re-selected while the
    measurement runs."""

    current: float = 0.0
    """The stripping current to apply.

    Note that this value acts as a multiplier in the applied current range.
    So if 10 µA is the applied current range and 1.5 is given as current value,
    the applied current will be 15 µA.

    If the stripping current is set to 0, chemical stripping is performed with a
    chemical oxidant or reductant. Otherwise the instrument acts as a galvanostat
    and applies a constant stripping current.

    The direction of the stripping current follows the sign of `end_potential`
    minus the deposition potential, or the sign of `end_potential` alone when no
    deposition time is used.
    """

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range."""

    end_potential: float = 0.0
    """Potential where the measurement stops in V.

    The measurement ends as soon as the measured potential drops below this value,
    even if `measurement_time` has not elapsed."""

    measurement_time: float = 1.0
    """The maximum measurement time in s.

    This value should always exceed the required measurement time.
    It only limits the time of the measurement.
    When the potential response is erroneously and `end_potential` is not reached within this time,
    the measurement is aborted."""

    bandwidth: None | float = None
    """Override bandwidth on MethodSCRIPT devices if set.

    Normally the instrument sets its filters optimally for the required bandwidth.
    When this is set, the bandwidth is overridden with the value in Hz. Only
    supported by MethodSCRIPT devices: e.g. Nexus, EmStat Pico and EmStat4 Series."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with stripping chrono potentiometry settings."""
        psmethod.RangingPotential = PalmSens.FixedPotentialRange(
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
    def _import(self, psmethod: PalmSens.Method, /):
        self.potential_range = pr_enum_to_string(psmethod.RangingPotential.StartPotentialRange)

        self.current = single_to_double(psmethod.Current)
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.measurement_time = single_to_double(psmethod.MeasurementTime)
        self.end_potential = single_to_double(psmethod.EndPotential)

        if psmethod.OverrideBandwidth:
            self.bandwidth = single_to_double(psmethod.Bandwidth)


class LinearSweepPotentiometry(
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
    BaseTechnique,
):
    """Create linear sweep potentiometry method parameters.

    Also known as Galvanodynamic Step. Supported by the Nexus series, PalmSens4 and
    EmStat4 LR and HR.

    LSP is the galvanostatic counterpart of
    [LinearSweepVoltammetry][pypalmsens.LinearSweepVoltammetry]: the current is
    swept from `current_begin` to `current_end` instead of the potential. The
    sweep is not truly linear but a series of `current_step` steps, and the
    potential is sampled during the last 25% of each step, so the current versus
    potential curve holds
    `(current_end - current_begin) / current_step + 1` points. The interval time
    between two points follows from `current_step / scan_rate`: with a
    `current_step` of 0.005 mA and a `scan_rate` of 0.1 mA/s the interval time is
    0.05 s.

    As with other galvanostatic techniques, LSP suits systems without a reference
    electrode whose electrochemical surface area is well known: the controlled
    current keeps the reaction rate stable, which helps for complex or multi-step
    reactions. Such sweeps are less prone to double-layer charging artefacts
    and potential drift than potentiodynamic ones.

    If an unknown current might drive the potential high enough to damage the
    working electrode, specify a maximum potential limit: the scan then stops
    early and `current_end` may not be reached. See
    [pypalmsens.settings.PotentialLimits][].

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.LinearSweepPotentiometry(
    ...     applied_current_range='100uA',
    ...     current_begin=-1.0,
    ...     current_end=1.0,
    ...     current_step=0.01,
    ...     scan_rate=1.0,
    ...     record_we_current=False,
    ... )
    """

    id: Literal['lsp'] = 'lsp'
    """Unique method identifier."""

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range."""

    current_begin: float = -1.0
    """Current applied at beginning of measurement.

    This value is multiplied by the defined current range and must stay within
    the applied current limits of the instrument, available as `min_current` and
    `max_current` on [pypalmsens.InstrumentManager.capabilities][]."""

    current_end: float = 1.0
    """Current applied at end of measurement.

    This value is multiplied by the defined current range and must stay within
    the applied current limits of the instrument. The scan stops early if a
    potential limit is reached before this current is applied."""

    current_step: float = 0.01
    """Current step.

    This value is multiplied by the defined current range.

    The minimum step is instrument dependent: 0.001 times the current range for
    PalmSens1 and 2, 0.00015 for PalmSens3, 0.000075 for PalmSens4, 0.000038 for
    Nexus, 0.0001 for EmStat4 LR and 0.000183 for EmStat4 HR."""

    scan_rate: float = 1.0
    """Scan rate in current per time.

    This value is multiplied by the defined current range, so with a `100uA`
    range a `scan_rate` of 1.0 sweeps 100 µA per second. The interval time of the
    recorded points is `current_step / scan_rate`.

    The applicable range depends on the value of `current_step` since the data
    acquisition rate is limited by the connected instrument."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record working electrode current."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.PotentialLimitsMixin,
    mixins.DataProcessingMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create multi-step potentiometry method parameters.

    Supported by the Nexus series, the PalmSens series and EmStat4 LR and HR.

    MultiStep Potentiometry lets you specify the number of current steps
    to apply and how long each step should last. The potential response is
    continuously sampled with the specified interval.

    A whole cycle of steps can be repeated several times.

    Levels can be specified using [pypalmsens.settings.ILevel][]. Each level can
    skip recording (`record`), move on to the next level once
    `limit_potential_max` or `limit_potential_min` is reached, and set digital
    trigger lines at its start.

    With a single level this is identical to
    [ChronoPotentiometry][pypalmsens.ChronoPotentiometry], which offers a larger
    range of measurement rates.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import ILevel
    >>> method = ps.MultiStepPotentiometry(
    ...     applied_current_range='1uA',
    ...     interval_time=0.1,
    ...     n_cycles=1,
    ...     levels=[
    ...         ILevel(level=0.0, duration=1.0, record=True)
    ...     ],
    ... )
    """

    id: Literal['mp'] = 'mp'
    """Unique method identifier."""

    applied_current_range: AllowedCurrentRanges = '1uA'
    """Applied current range."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    n_cycles: int = 1
    """Number of times the whole cycle of levels is repeated."""

    levels: list[ILevel] = Field(default_factory=lambda: [ILevel()])
    """The current levels to apply within a cycle, in order.

    Use [pypalmsens.settings.ILevel][] to create levels. Each level applies its
    current for its `duration` while the potential is sampled at `interval_time`.
    Switching between levels adds instrument overhead.
    """

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_we_current: bool = False
    """Record the working electrode current.

    The applied current between the working and the reference electrode, measured
    in `applied_current_range`."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with multistep potentiometry settings."""
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.IntervalTime = self.interval_time
        psmethod.nCycles = self.n_cycles
        psmethod.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            psmethod.Levels.Add(level._to_psobj())

        psmethod.UseSelectiveRecord = any(level.record for level in self.levels)
        psmethod.UseLimits = any(level.use_limits for level in self.levels)

        set_extra_value_mask(
            obj=psmethod,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)

        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.n_cycles = psmethod.nCycles

        self.levels = [ILevel._from_psobj(pslevel) for pslevel in psmethod.Levels]

        msk = get_extra_value_mask(psmethod)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


class ChronoCoulometry(
    mixins.CurrentRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.CurrentLimitsMixin,
    mixins.ChargeLimitsMixin,
    mixins.DataProcessingMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create chrono coulometry method parameters.

    Supported by the Nexus series, PalmSens3 and PalmSens4, the EmStat series and
    the Sensit series.

    Chronocoulometry (CC) and Chronoamperometry (CA) have the same potential waveform but
    in CC, the charge is monitored as a function of time (instead of the current).
    The charge is determined by integrating the current.

    While the current recorded in CA relates linearly to the reaction rate, the
    charge recorded in CC relates linearly to the number of converted reactants,
    as described by Faraday's law. This makes CC useful during deposition or
    electrochemical synthesis, and for characterising batteries and capacitors.

    The measurement is conducted in two steps: `step1_potential` at a potential
    where no reaction occurs, followed by `step2_potential` where the reaction is
    initiated, just like the classic Cottrell experiment. This ensures the charge
    step at the beginning is recorded.

    CC is also used to determine the number of adsorbed active species in a
    solution of freely diffusing species. Multiplying the Cottrell equation by t
    shows that the charge of the diffusing species is proportional to the square
    root of time, while the charge stored in the double layer and the charge of
    adsorbed species respond much faster. Plotting charge against the square root
    of time (an Anson plot) therefore ideally shows a jump in charge followed by a
    linear increase. Extrapolating the linear part back to the charge axis gives
    the combined double layer and adsorbed contribution, and a blank measurement
    separates the double layer contribution from the adsorbed one.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.ChronoCoulometry(
    ...     equilibration_time=0.0,
    ...     interval_time=0.1,
    ...     step1_potential=0.5,
    ...     step1_run_time=5.0,
    ...     step2_potential=0.5,
    ...     step2_run_time=5.0,
    ... )
    """

    id: Literal['cc'] = 'cc'
    """Unique method identifier."""

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """The time between two samples in s."""

    step1_potential: float = 0.5
    """Potential applied during first step in V.

    Use a potential at which no reaction occurs, so that the charge step at the
    start of the second step is recorded.

    Must stay within the potential limits of the instrument.
    See `min_potential` and `max_potential` on
    [pypalmsens.InstrumentManager.capabilities][]"""

    step1_run_time: float = 5.0
    """Run time for the first step.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (ca. 278 hours).
    """

    step2_potential: float = 0.5
    """Potential applied during second step in V.

    The potential at which the reaction is initiated. Subject to the same
    instrument potential limits as `step1_potential`."""

    step2_run_time: float = 5.0
    """Run time for the second step.

    The minimum and maximum duration of a measurement:
    5 * `interval_time` to 1,000,000 seconds (ca. 278 hours).
    """

    bandwidth: None | float = None
    """Override bandwidth on MethodSCRIPT devices if set.

    Normally the instrument sets its filters optimally for the required bandwidth.
    When this is set, the bandwidth is overridden with the value in Hz. Only
    supported by MethodSCRIPT devices: e.g. Nexus, EmStat Pico and (Multi)EmStat4."""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_potential: bool = False
    """Record applied working electrode potential.

    Reference electrode vs ground."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
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
    def _import(self, psmethod: PalmSens.Method, /):
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
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.MeasurementTriggersMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MaterialMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create electrochemical impedance spectroscopy method parameters.

    Electrochemical Impedance Spectroscopy (EIS) is an electrochemical technique to measure
    the impedance of a system in dependence of the frequency of the applied AC signal.

    Although "spectroscopy" implies a frequency sweep, which is the most common
    measurement, this class provides the flexibility to set the frequency and vary
    other parameters, such as DC potential and time.

    Every measurement point yields the impedance `Z = E_ac / I_ac` at the applied
    frequency. The impedance is a complex number `Z = Z' − jZ''`, with the real part
    `Z'` and the imaginary part `Z''`, at the angular frequency `ω = 2πf`. The phase
    shift follows `tan(φ) = −Z'' / Z'` and the magnitude `|Z|² = Z'² + Z''²`.

    A spectrum is usually presented as a Nyquist plot of `Z''` against `Z'`, or as a
    Bode plot of `log|Z|` and the phase shift against `log f`. The admittance, the
    inverse of the impedance `Y = 1 / Z = Y' + jY''`, is plotted instead as `Y`
    against `log f` or `Y''` against `Y'`.

    Available modes of EIS measurements:

    - a frequency scan at a fixed dc-potential (default EIS)
    - frequency scans at each dc-potential in a potential scan
    - frequency scans at specified time intervals (time scan)
    - a single frequency applied at each dc potential in a potential scan (Mott-Schottky)
    - a repeated single frequency at specified time intervals

    EIS can also be used to study corrosion and the effects of coatings.
    For example, anodized coatings, conversion coatings or organic coatings like paints.

    The applied frequencies must stay within the EIS frequency range of the
    instrument, see [pypalmsens.InstrumentManager.capabilities][]
    (`eis_min_frequency` / `eis_max_frequency`).

    During EIS the instrument selects the current range automatically, so it is
    generally best to enable all ranges in
    [pypalmsens.settings.CurrentRange][]: the highest usable range follows from
    the lowest impedance to be measured (`1 / Z`) together with the highest
    dc-current, and the lowest usable range from the highest impedance and the
    lowest dc-current. Some ranges can still be unavailable because of
    `max_frequency` or `ac_potential`. The measurement starts in the highest
    enabled range and searches for a suitable range from the top down, which is
    quick when the scan starts above 1 kHz; starting below 1 Hz makes each point
    much longer and may need extra time on the first point, so a single fixed
    range can be simpler for a low-frequency time scan.

    Leave the higher ranges enabled when you measure at high frequencies. The
    auto-ranging routine determines the gain from the maximum bandwidth, which
    combines switching to the optimal range with a gain of 10 or 100 on the
    active range, so excluding a range can leave too little bandwidth to sample
    the high frequencies accurately.

    Pretreatment always runs in potentiostatic mode, also for
    [pypalmsens.GalvanostaticImpedanceSpectroscopy][], and `equilibration_time`
    elapses before the impedance measurement at each newly applied dc-potential.

    Examples
    --------
    EIS with frequency scan:

    >>> import pypalmsens as ps
    >>> method = ps.ElectrochemicalImpedanceSpectroscopy(
    ...     frequency_type='scan',
    ...     min_frequency=5.0,
    ...     max_frequency=10000,
    ...     n_frequencies=11,
    ...     scan_type='fixed',
    ...     min_sampling_time=0.5,
    ...     max_equilibration_time=5.0,
    ... )

    EIS with frequency scans repeated over a range of DC potential values:

    >>> method = ps.ElectrochemicalImpedanceSpectroscopy(
    ...     frequency_type='scan',
    ...     min_frequency=5.0,
    ...     max_frequency=10000,
    ...     n_frequencies=11,
    ...     scan_type='potential',
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     min_sampling_time=0.5,
    ...     max_equilibration_time=5.0,
    ... )

    EIS with frequency scans repeated for 10 seconds (`run_time`):

    >>> method = ps.ElectrochemicalImpedanceSpectroscopy(
    ...     frequency_type='scan',
    ...     min_frequency=5.0,
    ...     max_frequency=10000,
    ...     n_frequencies=11,
    ...     scan_type='time',
    ...     run_time=10,
    ...     min_sampling_time=0.5,
    ...     max_equilibration_time=5.0,
    ... )
    """

    id: Literal['eis'] = 'eis'
    """Unique method identifier."""

    _SCAN_TYPES: tuple[AllowedScanTypes, ...] = (
        'potential',
        'time',
        'fixed',
    )
    _FREQ_TYPES: tuple[AllowedFrequencyTypes, ...] = ('fixed', 'scan')

    equilibration_time: float = 0.0
    """Equilibration time in s.

    Each time a new dc-potential is applied, this time elapses before the
    impedance measurements for that potential start."""

    dc_potential: float = 0.0
    """DC-potential applied during the EIS scan in V.

    Also called _DC Bias_ or _level_.
    The most common setting for this parameter is 0 V vs. OCP.

    Must stay within the potential range of the instrument, see
    [pypalmsens.InstrumentManager.capabilities][]
    (`min_potential` / `max_potential`).
    """

    ac_potential: float = 0.01
    """AC potential in V RMS.

    The amplitude of the ac potential signal has a range of 0.001 V to 0.25 V
    (RMS). In many applications, a value of 0.010 V (RMS) is used.

    The maximum amplitude of your instrument is available as
    `max_eis_amplitude_erms` on
    [pypalmsens.InstrumentManager.capabilities][]. Together with `max_frequency`
    this amplitude can make some current ranges unavailable.

    Keep the amplitude small: an amplitude that leaves the linear region of the
    system produces higher harmonics of the applied frequency and can start redox
    reactions. Raise it only for very high impedances, in the megaohm range and
    above, where the resulting current stays small enough to remain linear."""

    frequency_type: AllowedFrequencyTypes = 'scan'
    """Whether to measure a single frequency or scan over a range of frequencies.

    Possible values: 'scan', 'fixed'.

    - Scan: a frequency scan is performed starting at the given `max_frequency`
        down to `min_frequency`. This is the setting for a regular EIS experiment.
    - Fixed: a single frequency given by `fixed_frequency` is applied for
        the given duration or at each dc-potential step or time interval.
    """

    fixed_frequency: float = 1_000
    """Fixed frequency in Hz (`frequency_type='fixed'`).

    Applied at each dc-potential step or time interval when `scan_type` is
    `'potential'` or `'time'`. Must be within the EIS frequency range of the
    instrument, see [pypalmsens.InstrumentManager.capabilities][]
    (`eis_min_frequency` / `eis_max_frequency`)."""

    min_frequency: float = 5.0
    """Frequency the frequency scan ends on in Hz (frequency scan only).

    Must stay within the EIS frequency range of the instrument, see
    [pypalmsens.InstrumentManager.capabilities][] (`eis_min_frequency`)."""

    max_frequency: float = 10_000
    """Frequency the frequency scan starts on in Hz (frequency scan only).

    The scan runs from here down to `min_frequency`. Above 1 kHz a point is
    measured in a few seconds; below 1 Hz each point takes much longer and the
    first point may need extra time to select a current range. Must stay within
    the EIS frequency range of the instrument, see
    [pypalmsens.InstrumentManager.capabilities][] (`eis_max_frequency`)."""

    n_frequencies: int = 11
    """Number of frequencies to apply in the frequency scan (frequency scan only).

    Defines the frequencies to apply between the `max_frequency` and
    `min_frequency`. For example, a value of 11 will measure at 11 frequencies,
    including both end points.

    EIS experiments usually span kilohertz to millihertz, so a logarithmic
    spacing is common: 10 frequencies per decade makes a scan from 10 kHz down
    to 100 Hz 2 decades times 10 + 1 frequencies, i.e. 21 frequencies.

    This is the total number of applied frequencies, not the number per decade.
    """

    scan_type: AllowedScanTypes = 'fixed'
    """Whether a single or multiple frequency scans are performed.

    Possible values: 'potential', 'time', 'fixed'.

    - Fixed scan: perform a single scan (default). `dc_potential` stays fixed
        during the scan.
    - Time scan: scans are repeated for a specific amount of time at a specific interval.
    - Potential scan: scans are repeated over a range of DC potential values,
        starting at `begin_potential` and ending at `end_potential` in steps of
        `step_potential`. At each dc-potential level a single fixed frequency or a
        full frequency scan is applied, according to `frequency_type`.
        A potential scan should not be performed versus the OCP.
    """

    run_time: float = 10.0
    """Minimal run time in seconds in s (time scan only).

    Scans are repeated until this much time has elapsed, within the run time the
    instrument allows: less than 1 s up to 1,000,000 s. For example, if a
    frequency scan takes 10 seconds and is measured at an interval of 1 second
    for a `run_time` of 25 seconds, then three iterations will be performed."""

    interval_time: float = 0.1
    """The interval at which a measurement iteration should be performed in s (time scan only).

    The minimum interval time between each data point (`frequency_type='fixed'`) or
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
    Must stay within the potential range of the instrument, see
    [pypalmsens.InstrumentManager.capabilities][] (`min_potential` / `max_potential`).
    """

    end_potential: float = 0.0
    """The dc-potential at which the scan ends in V (potential scan only).

    I.e. the DC potential of the applied sine wave at which the series of iterative measurements ends.
    The applicable range is the same as for `begin_potential`.
    """

    step_potential: float = 0.01
    """Potential step size in V (potential scan only).

    This sets the increment to be used between `begin_potential` and `end_potential`.
    The largest step is 250 mV, the smallest step your instrument allows is
    `min_potential_step` in mV on
    [pypalmsens.InstrumentManager.capabilities][].
    """

    min_sampling_time: float = Field(default=0.5, gt=0)
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

    Increasing this parameter can be beneficial when measuring unstable or
    noisy samples at low frequencies, although it extends the overall
    measurement time.
    """

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with electrochemical impedance spectroscopy settings."""

        if self.scan_type == 'potential':
            # psmethod.BeginPotential is an alias for psmethod.Potential
            psmethod.BeginPotential = self.begin_potential
            psmethod.EndPotential = self.end_potential
            psmethod.StepPotential = self.step_potential
        elif self.scan_type == 'time':
            psmethod.RunTime = self.run_time
            psmethod.IntervalTime = self.interval_time
            psmethod.Potential = self.dc_potential
        else:
            psmethod.Potential = self.dc_potential

        psmethod.ScanType = enumScanType(self._SCAN_TYPES.index(self.scan_type))
        psmethod.FreqType = enumFrequencyType(self._FREQ_TYPES.index(self.frequency_type))
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.Eac = self.ac_potential
        psmethod.FixedFrequency = self.fixed_frequency
        psmethod.MaxFrequency = self.max_frequency
        psmethod.MinFrequency = self.min_frequency
        psmethod.nFrequencies = self.n_frequencies
        psmethod.SamplingTime = self.min_sampling_time
        psmethod.MaxEqTime = self.max_equilibration_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.scan_type = self._SCAN_TYPES[int(psmethod.ScanType)]
        self.frequency_type = self._FREQ_TYPES[int(psmethod.FreqType)]
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.dc_potential = single_to_double(psmethod.Potential)
        self.ac_potential = single_to_double(psmethod.Eac)
        self.n_frequencies = psmethod.nFrequencies
        self.min_sampling_time = single_to_double(psmethod.SamplingTime)
        self.max_equilibration_time = single_to_double(psmethod.MaxEqTime)

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
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.VersusOCPMixin,
    mixins.PostMeasurementMixin,
    mixins.MeasurementTriggersMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create fast impedance spectroscopy method parameters.

    Fast EIS applies a single frequency at `dc_potential` and repeats it every
    `interval_time`, following rapid impedance changes of a cell instead of
    sweeping a spectrum. The latency between data points is reduced to a minimum
    of 1 ms, and the instrument buffers the points in its internal memory: no
    points are shown while the measurement runs, the full dataset is transferred
    and plotted once it completes.

    Because a lower frequency needs a longer wave period, the shortest interval
    depends on the applied frequency: the 1 ms minimum requires 10 kHz or higher,
    and the relation is not linear, as a 10 ms interval allows frequencies down
    to 250 Hz.

    Only the EmStat4 series and the Nexus series support this technique.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.FastImpedanceSpectroscopy(
    ...     equilibration_time=0.0,
    ...     interval_time=0.1,
    ...     run_time=10.0,
    ...     dc_potential=0.0,
    ...     ac_potential=0.01,
    ...     frequency=50000.0,
    ... )
    """

    id: Literal['fis'] = 'fis'
    """Unique method identifier."""

    equilibration_time: float = 0.0
    """Equilibration time in s.

    `dc_potential` is applied and held for this long before the first sample."""

    interval_time: float = 0.1
    """The time between two samples in s.

    The minimum depends on the applied frequency: 1 ms requires 10 kHz or higher,
    and the relation is not linear, as a 10 ms interval allows frequencies down
    to 250 Hz."""

    run_time: float = 10.0
    """Total run time of the measurement in s."""

    dc_potential: float = 0.0
    """Potential applied during the measurement in V.

    Must stay within the potential range of the instrument, see
    [pypalmsens.InstrumentManager.capabilities][]
    (`min_potential` / `max_potential`)."""

    ac_potential: float = 0.01
    """Potential amplitude in V (RMS).

    The range is 0.001 V to 0.25 V (RMS), commonly 0.010 V. The maximum of your
    instrument is `max_eis_amplitude_erms` on
    [pypalmsens.InstrumentManager.capabilities][]."""

    frequency: float = 50000.0
    """Fixed frequency in Hz, applied at every `interval_time`.

    Must stay within the EIS frequency range of the instrument, see
    [pypalmsens.InstrumentManager.capabilities][] (`eis_min_frequency` /
    `eis_max_frequency`)."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with fast impedance spectroscopy settings."""
        psmethod.Eac = self.ac_potential
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.FixedFrequency = self.frequency
        psmethod.IntervalTime = self.interval_time
        psmethod.Potential = self.dc_potential
        psmethod.RunTime = self.run_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.ac_potential = single_to_double(psmethod.Eac)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.frequency = single_to_double(psmethod.FixedFrequency)
        self.interval_time = single_to_double(psmethod.IntervalTime)
        self.dc_potential = single_to_double(psmethod.Potential)
        self.run_time = single_to_double(psmethod.RunTime)


class GalvanostaticImpedanceSpectroscopy(
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.EquilibrationTriggersMixin,
    mixins.MeasurementTriggersMixin,
    mixins.MultiplexerMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create galvanostatic impedance spectroscopy method parameters.

    In Galvanostatic EIS (GEIS) the current through the cell is controlled rather
    than the potential across it, which is preferred for low-impedance cells. To
    keep currents small on a low impedance a potentiostatic measurement uses a
    small amplitude, but a cell whose impedance changes during the measurement
    then produces unexpected currents. In galvanostatic mode the amplitude of the
    AC current is controlled and set by the user.

    The current follower is part of the controlled loop, so current ranges cannot
    be switched while measuring: auto current ranging is not supported in
    galvanostatic mode and `applied_current_range` must cover the whole
    measurement. Pretreatment is still applied in potentiostatic mode.

    For GEIS the modes are:

    - a frequency scan at a fixed dc-current
    - frequency scans at each current in a current scan
    - frequency scans at specified time intervals (time scan)
    - a single frequency applied at each current in a current scan
    - a single frequency at specified time intervals

    Because the bandwidth of the current follower affects the stability of the
    system, the maximum frequency is limited to 100 kHz on PalmSens4.

    Examples
    --------
    GEIS with frequency scan:

    >>> import pypalmsens as ps
    >>> method = ps.GalvanostaticImpedanceSpectroscopy(
    ...     applied_current_range='10uA',
    ...     frequency_type='scan',
    ...     min_frequency=5.0,
    ...     max_frequency=10000,
    ...     n_frequencies=11,
    ...     scan_type='fixed',
    ...     dc_current=0.0,
    ...     ac_current=0.01,
    ...     min_sampling_time=0.5,
    ...     max_equilibration_time=5.0,
    ... )

    GEIS with frequency scans repeated over a range of current values:

    >>> method = ps.GalvanostaticImpedanceSpectroscopy(
    ...     applied_current_range='10uA',
    ...     frequency_type='scan',
    ...     min_frequency=5.0,
    ...     max_frequency=10000,
    ...     n_frequencies=11,
    ...     scan_type='current',
    ...     begin_current=0.0,
    ...     step_current=0.01,
    ...     end_current=1.0,
    ...     ac_current=0.01,
    ...     min_sampling_time=0.5,
    ...     max_equilibration_time=5.0,
    ... )

    GEIS with frequency scans repeated for 10 seconds (`run_time`):

    >>> method = ps.GalvanostaticImpedanceSpectroscopy(
    ...     applied_current_range='10uA',
    ...     frequency_type='scan',
    ...     min_frequency=5.0,
    ...     max_frequency=10000,
    ...     n_frequencies=11,
    ...     scan_type='time',
    ...     run_time=10.0,
    ...     interval_time=0.1,
    ...     dc_current=0.0,
    ...     ac_current=0.01,
    ...     min_sampling_time=0.5,
    ...     max_equilibration_time=5.0,
    ... )
    """

    id: Literal['gis'] = 'gis'
    """Unique method identifier."""

    _SCAN_TYPES: tuple[AllowedScanTypes, ...] = (
        'current',
        'time',
        'fixed',
    )
    _FREQ_TYPES: tuple[AllowedFrequencyTypes, ...] = ('fixed', 'scan')

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range.

    Current values (such as `ac_current`, `begin_current` or `step_current`) are
    expressed as a factor of this range.

    Auto current ranging is not possible in galvanostatic mode, so this range has
    to cover all currents of the measurement."""

    equilibration_time: float = 0.0
    """Equilibration time in s.

    Each time a new dc-current is applied, this time elapses before the impedance
    measurements for that current start."""

    ac_current: float = 0.01
    """AC current amplitude as a factor of `applied_current_range`, in RMS.

    On PalmSens4 the maximum factor is 0.4 per current range, except for the
    10 mA range where it is 0.2."""

    dc_current: float = 0.0
    """DC current applied during the GEIS scan as a factor of `applied_current_range`."""

    frequency_type: AllowedFrequencyTypes = 'scan'
    """Whether to measure a single frequency or scan over a range of frequencies.

    Possible values: 'scan', 'fixed'.

    - Scan: a frequency scan is performed starting at the given `max_frequency`
        down to `min_frequency`. This is the setting for a regular GEIS experiment.
    - Fixed: a single frequency given by `fixed_frequency` is applied for
        the given duration or at each current step or time interval.
    """

    fixed_frequency: float = 1_000
    """Fixed frequency in Hz (`frequency_type='fixed'`).

    Applied at each current step or time interval when `scan_type` is `'current'`
    or `'time'`. Must be within the impedance frequency range of the instrument,
    see [pypalmsens.InstrumentManager.capabilities][]."""

    min_frequency: float = 5.0
    """Frequency the frequency scan ends on in Hz (frequency scan only)."""

    max_frequency: float = 10_000
    """Frequency the frequency scan starts on in Hz (frequency scan only).

    The scan runs from here down to `min_frequency`. In galvanostatic mode the
    bandwidth of the current follower limits the stability.
    The limit of your instrument is `geis_max_frequency` on
    [pypalmsens.InstrumentManager.capabilities][]."""

    n_frequencies: int = 11
    """Number of frequencies to apply in the frequency scan (frequency scan only).

    Defines the frequencies to apply between the `max_frequency` and
    `min_frequency`. For example, a value of 11 will measure at 11 frequencies,
    including both end points.

    This is the total number of applied frequencies, not the number per decade.
    """

    scan_type: AllowedScanTypes = 'fixed'
    """Whether a single or multiple frequency scans are performed.

    Possible values: 'current', 'time', 'fixed'.

    - Fixed scan: perform a single scan (default). `dc_current` stays fixed
        during the scan.
    - Time scan: scans are repeated for a specific amount of time at a specific interval.
    - Current scan: scans are repeated over a range of current values, starting at
        `begin_current` and ending at `end_current` in steps of `step_current`.
        At each dc-current level a single fixed frequency or a full frequency scan
        is applied, according to `frequency_type`.
    """

    run_time: float = 10.0
    """Minimal run time in seconds in s (time scan only).

    Scans are repeated until this much time has elapsed, within the run time the
    instrument allows: less than 1 s up to 1,000,000 s. For example, if a
    frequency scan takes 10 seconds and is measured at an interval of 1 seconds
    for a `run_time` of 25 seconds, then three iterations will be performed."""

    interval_time: float = 0.1
    """The interval at which a measurement iteration should be performed in s (time scan only).

    The minimum interval time between each data point (`frequency_type='fixed'`) or
    between each frequency scan (`frequency_type='scan'). In galvanostatic mode the
    interval cannot be lower than the time needed to measure the data point or to
    perform the frequency scan, plus the overhead time.

    If a measurement iteration takes longer than the interval time the next measurement
    will not be triggered until after it has been completed.
    """

    begin_current: float = 0.0
    """Current at which the scan starts expressed in the applied current range (current scan only)."""

    end_current: float = 0.0
    """Current at which the scan ends expressed in the applied current range (current scan only).

    The applicable range is the same as for `begin_current`."""

    step_current: float = 0.01
    """Current step size expressed in the applied current range (current scan only).

    This sets the increment to be used between `begin_current` and `end_current`.
    The smallest step is instrument-specific: from 0.000038 times the applied
    current range on Nexus to 0.000183 times on EmStat4 HR."""

    min_sampling_time: float = Field(0.5, gt=0)
    """Minimum sampling time in s.

    Each measurement point of the impedance spectrum is performed
    during the period specified by `min_sampling_time`.

    This means that the number of measured sine waves is equal to `min_sampling_time * frequency`.
    If this value is less than 1 sine wave, the sampling is extended to `1 / frequency`.

    So for a measurement at a `frequency`, at least one complete sine wave is measured.
    Reasonable values for the sampling are in the range of 0.1 to 1 s.

    Increasing it can stabilise inconsistent points in the high-frequency
    region."""

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

    Increasing this parameter can be beneficial when measuring unstable or
    noisy samples at low frequencies, although it extends the overall
    measurement time.
    """

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with galvanic impedance spectroscopy settings."""

        if self.scan_type == 'current':
            # psmethod.BeginCurrent is an alias for psmethod.Current
            psmethod.BeginCurrent = self.begin_current
            psmethod.EndCurrent = self.end_current
            psmethod.StepCurrent = self.step_current
        elif self.scan_type == 'time':
            psmethod.RunTime = self.run_time
            psmethod.IntervalTime = self.interval_time
            psmethod.Idc = self.dc_current
        else:
            psmethod.Idc = self.dc_current

        psmethod.ScanType = enumScanType(self._SCAN_TYPES.index(self.scan_type))
        psmethod.FreqType = enumFrequencyType(self._FREQ_TYPES.index(self.frequency_type))
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.EquilibrationTime = self.equilibration_time
        psmethod.Iac = self.ac_current
        psmethod.FixedFrequency = self.fixed_frequency
        psmethod.nFrequencies = self.n_frequencies
        psmethod.MaxFrequency = self.max_frequency
        psmethod.MinFrequency = self.min_frequency
        psmethod.SamplingTime = self.min_sampling_time
        psmethod.MaxEqTime = self.max_equilibration_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.scan_type = self._SCAN_TYPES[int(psmethod.ScanType)]
        self.frequency_type = self._FREQ_TYPES[int(psmethod.FreqType)]
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.equilibration_time = single_to_double(psmethod.EquilibrationTime)
        self.ac_current = single_to_double(psmethod.Iac)
        self.dc_current = single_to_double(psmethod.Idc)
        self.n_frequencies = psmethod.nFrequencies
        self.min_sampling_time = single_to_double(psmethod.SamplingTime)
        self.max_equilibration_time = single_to_double(psmethod.MaxEqTime)

        self.fixed_frequency = single_to_double(psmethod.FixedFrequency)
        self.max_frequency = single_to_double(psmethod.MaxFrequency)
        self.min_frequency = single_to_double(psmethod.MinFrequency)

        if self.scan_type == 'current':
            self.begin_current = single_to_double(psmethod.BeginCurrent)
            self.end_current = single_to_double(psmethod.EndCurrent)
            self.step_current = single_to_double(psmethod.StepCurrent)
        elif self.scan_type == 'time':
            self.run_time = single_to_double(psmethod.RunTime)
            self.interval_time = single_to_double(psmethod.IntervalTime)


class FastGalvanostaticImpedanceSpectroscopy(
    mixins.CurrentRangeMixin,
    mixins.PotentialRangeMixin,
    mixins.PretreatmentMixin,
    mixins.PostMeasurementMixin,
    mixins.GeneralMixin,
    BaseTechnique,
):
    """Create fast galvanostatic impedance spectroscopy method parameters.

    Fast GEIS applies a single frequency and repeats it every `interval_time`
    while the current through the cell is controlled rather than the potential.
    As in [pypalmsens.GalvanostaticImpedanceSpectroscopy][] the currents are
    factors of `applied_current_range`, and auto current ranging is unavailable.

    As in [pypalmsens.FastImpedanceSpectroscopy][] the latency between points is
    reduced to a minimum of 1 ms and the instrument buffers the points in its
    internal memory, so nothing is shown during the measurement. The shortest
    interval depends on the frequency: 10 kHz or higher for 1 ms, while a 10 ms
    interval allows frequencies down to 250 Hz.

    Only the EmStat4 series and the Nexus series support this technique.

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.FastGalvanostaticImpedanceSpectroscopy(
    ...     applied_current_range='100uA',
    ...     run_time=10.0,
    ...     interval_time=0.1,
    ...     ac_current=0.01,
    ...     dc_current=0.0,
    ...     frequency=50000.0,
    ... )
    """

    id: Literal['fgis'] = 'fgis'
    """Unique method identifier."""

    applied_current_range: AllowedCurrentRanges = '100uA'
    """Applied current range.

    The current values below are expressed as a factor of this range. The ranges
    your instrument can apply are `supported_applied_current_ranges` on
    [pypalmsens.InstrumentManager.capabilities][]. Auto current ranging is not
    possible in galvanostatic mode, so this range has to cover all currents of
    the measurement."""

    run_time: float = 10.0
    """Total run time of the measurement in s."""

    interval_time: float = 0.1
    """The time between two samples in s.

    The minimum depends on the applied frequency: 1 ms requires 10 kHz or higher,
    and the relation is not linear, as a 10 ms interval allows frequencies down
    to 250 Hz."""

    ac_current: float = 0.01
    """AC current amplitude as a factor of `applied_current_range`, in RMS."""

    dc_current: float = 0.0
    """DC current applied during the measurement as a factor of `applied_current_range`."""

    frequency: float = 50000.0
    """Fixed frequency in Hz, applied at every `interval_time`.

    Must stay within the impedance frequency range of your instrument, limited by
    `geis_max_frequency` on [pypalmsens.InstrumentManager.capabilities][]."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with fast galvanic impedance spectroscopy settings."""
        psmethod.AppliedCurrentRange = cr_string_to_enum(self.applied_current_range)
        psmethod.Iac = self.ac_current
        psmethod.Idc = self.dc_current
        psmethod.FixedFrequency = self.frequency
        psmethod.RunTime = self.run_time
        psmethod.IntervalTime = self.interval_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.applied_current_range = cr_enum_to_string(psmethod.AppliedCurrentRange)
        self.ac_current = single_to_double(psmethod.Iac)
        self.dc_current = single_to_double(psmethod.Idc)
        self.frequency = single_to_double(psmethod.FixedFrequency)
        self.run_time = single_to_double(psmethod.RunTime)
        self.interval_time = single_to_double(psmethod.IntervalTime)


class MethodScript(BaseTechnique):
    """Create a MethodSCRIPT method.

    With the MethodSCRIPT scripting language, you can write code that runs on-device. This
    enables custom measurements and makes it possible to combine different measurements
    and other tasks. The script is programmed directly into the potentiostat,
    so the measurement sequence itself runs on the instrument.

    This class uses the PyPalmSens machinery to send your MethodSCRIPT script directly
    to the potentiostat.

    Running a script requires an instrument that supports MethodSCRIPT: Nexus, EmStat4,
    EmStat Pico, and the Sensit series.

    See [the MethodSCRIPT documentation](https://www.palmsens.com/methodscript/) for more
    information and script examples.

    Examples
    --------
    Return hello world:

    >>> import pypalmsens as ps
    >>> from textwrap import dedent
    >>> method = ps.MethodScript(
    ...     script=dedent('''\\
    ...        wait 100m
    ...        if 1 < 2
    ...            send_string "Hello world"
    ...        endif
    ...     ''')
    ... )

    Chronoamperometry measurement loop example:

    >>> method = ps.MethodScript(
    ...     script=dedent('''\\
    ...         var potential
    ...         var current
    ...         set_pgstat_chan 0
    ...         set_pgstat_mode 2
    ...         cell_on
    ...         meas_loop_ca potential current 100m 200m 1000m
    ...             pck_start
    ...             pck_add potential
    ...             pck_add current
    ...             pck_end
    ...         endloop
    ...     ''')
    ... )
    """

    id: Literal['ms'] = 'ms'
    """Unique method identifier."""

    version: Literal['1.10'] | None = '1.10'
    """MethodSCRIPT language version.

    Determines the version of the MethodSCRIPT parser to use for validating
    the syntax of `script`. Set to `None` to skip script validation.
    """

    script: str = """\
wait 100m
if 1 < 2
    send_string "Hello world"
endif
"""
    """Script to run.

    A leading `e` line and trailing whitespace are removed, and the result is
    validated against the parser selected by `version`.

    For more info on MethodSCRIPT, see
    [the MethodSCRIPT documentation](https://www.palmsens.com/methodscript/)."""

    custom_units: dict[Literal['as', 'at', 'au'], CustomUnits] = Field(default_factory=dict)
    """Define custom quantities and units for 'as', 'at', 'au' variable types.

    Use this to override the quantities for analog inputs (0, 1, and 2).
    These default to Voltage / V. Defining custom units is purely cosmetic.
    The values are used for labeling curves and axes."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        """Update method with MethodScript."""
        psmethod.MethodScript = f'e\n{self.script}\n'

        for name, unit in self.custom_units.items():
            if name == 'as':
                psmethod.OverrideUnitForASVarType = True
                psmethod.CustomUnitASVarTypeQuantity = unit.quantity
                psmethod.CustomUnitASVarTypeSymbol = unit.symbol
                psmethod.CustomUnitASVarTypeUnit = unit.unit
            elif name == 'at':
                psmethod.OverrideUnitForATVarType = True
                psmethod.CustomUnitATVarTypeQuantity = unit.quantity
                psmethod.CustomUnitATVarTypeSymbol = unit.symbol
                psmethod.CustomUnitATVarTypeUnit = unit.unit
            elif name == 'au':
                psmethod.OverrideUnitForAUVarType = True
                psmethod.CustomUnitAUVarTypeQuantity = unit.quantity
                psmethod.CustomUnitAUVarTypeSymbol = unit.symbol
                psmethod.CustomUnitAUVarTypeUnit = unit.unit

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.script = psmethod.MethodScript

        if psmethod.OverrideUnitForATVarType:
            self.custom_units['as'] = CustomUnits(
                quantity=psmethod.CustomUnitASVarTypeQuantity,
                symbol=psmethod.CustomUnitASVarTypeSymbol,
                unit=psmethod.CustomUnitASVarTypeUnit,
            )

        if psmethod.OverrideUnitForATVarType:
            self.custom_units['at'] = CustomUnits(
                quantity=psmethod.CustomUnitATVarTypeQuantity,
                symbol=psmethod.CustomUnitATVarTypeSymbol,
                unit=psmethod.CustomUnitATVarTypeUnit,
            )

        if psmethod.OverrideUnitForAUVarType:
            self.custom_units['au'] = CustomUnits(
                quantity=psmethod.CustomUnitAUVarTypeQuantity,
                symbol=psmethod.CustomUnitAUVarTypeSymbol,
                unit=psmethod.CustomUnitAUVarTypeUnit,
            )

    @classmethod
    def from_file(cls, path: str | Path = 'methodscript.mscr') -> MethodScript:
        """Load a MethodSCRIPT from a file.

        Parameters
        ----------
        path: str | Path
            Path to a MethodSCRIPT file, normally with the `.mscr` extension.

        Returns
        -------
        method: MethodScript
        """
        with Path(path).open('r') as f:
            script = f.read()

        return cls(script=script)

    def to_file(self, path: str | Path = 'methodscript.mscr') -> None:
        """Save the script to a file.

        Parameters
        ----------
        path: str | Path
            Path to write the MethodSCRIPT to, normally with the `.mscr`
            extension.
        """
        with Path(path).open('w') as f:
            _ = f.write(self.script)

    @classmethod
    def from_url(cls, url: str) -> MethodScript:
        """Download a script over http(s).

        Parameters
        ----------
        url : url
            URL to download the MethodSCRIPT file from.

        Returns
        -------
        method: MethodScript
        """
        with urllib.request.urlopen(url) as response:
            script = response.read().decode()

        return cls(script=script)

    @field_validator('script')
    @classmethod
    def validate_script(cls, value: str) -> str:
        if value.startswith('e\n'):
            value = value.replace('e\n', '', 1)

        value = value.rstrip()
        value += '\n'

        return value

    @model_validator(mode='after')
    def validate_script_parser(self) -> Self:
        if self.version == '1.10':
            validate_methodscript(self.script)

        return self

    @property
    @override
    def _use_hardware_sync(self) -> bool:
        """Return true if 'set_channel_sync 1' is set."""
        match = re.findall(r'^\s*(set_channel_sync\s+1)', self.script)

        return any(match)
