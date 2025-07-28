from dataclasses import dataclass, field

from PalmSens import Method as PSMethod
from PalmSens import Techniques
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType

from ._shared import (
    ELevel,
    get_current_range,
    get_extra_value_mask,
    set_extra_value_mask,
)
from .settings import (
    AutorangingCurrentSettings,
    AutorangingPotentialSettings,
    BipotSettings,
    ChargeLimitSettings,
    CurrentLimitSettings,
    FilterSettings,
    IrDropCompensationSettings,
    MultiplexerSettings,
    OtherSettings,
    PostMeasurementSettings,
    PotentialLimitSettings,
    PretreatmentSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    VersusOcpSettings,
)


class BaseParameters:
    """Provide generic methods for interacting with the PalmSens.Method
    object."""

    _PSMethod: PSMethod = PSMethod

    def to_psobj(self):
        """Convert parameters to dotnet method."""
        obj = self._PSMethod()

        for parent in self.__class__.__mro__:
            if parent in (object, BaseParameters):
                continue
            parent.update_psobj(self, obj=obj)

        return obj

    @classmethod
    def from_psobj(cls, obj: PSMethod):
        """Generate parameters from dotnet method."""
        new = cls()

        for parent in cls.__mro__:
            if parent in (object, BaseParameters):
                continue
            new.update_params(obj=obj)

        return new

    def update_params(self, *, obj): ...


@dataclass
class CyclicVoltammetryParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    PretreatmentSettings,
    VersusOcpSettings,
    PostMeasurementSettings,
    CurrentLimitSettings,
    IrDropCompensationSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    OtherSettings,
):
    """Create cyclic voltammetry method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    begin_potential: float
        Begin potential in V (default: -0.5)
    vertex1_potential: float
        Vertex 1 potential in V (default: 0.5)
    vertex2_potential: float
        Vertex 2 potential in V (default: -0.5)
    step_potential: float
        Step potential in V (default: 0.1)
    scanrate: float
        Scan rate in V/s (default: 1.0)
    n_scans: float
        Number of scans (default: 1)
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False)
        Counter electrode vs ground.
    record_we_potential : bool
        Record applied working electrode potential (default: False)
        Reference electrode vs ground.
    """

    _PSMethod = Techniques.CyclicVoltammetry

    equilibration_time: float = 0.0
    begin_potential: float = -0.5
    vertex1_potential: float = 0.5
    vertex2_potential: float = -0.5
    step_potential: float = 0.1
    scanrate: float = 1.0
    n_scans: float = 1

    enable_bipot_current: bool = False
    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False

    def update_psobj(self, *, obj):
        """Update method with cyclic voltammetry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.Vtx1Potential = self.vertex1_potential
        obj.Vtx2Potential = self.vertex2_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate
        obj.nScans = self.n_scans

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    def update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.begin_potential = obj.BeginPotential
        self.vertex1_potential = obj.Vtx1Potential
        self.vertex2_potential = obj.Vtx2Potential
        self.step_potential = obj.StepPotential
        self.scanrate = obj.Scanrate
        self.n_scans = obj.nScans

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class LinearSweepParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    PretreatmentSettings,
    VersusOcpSettings,
    BipotSettings,
    PostMeasurementSettings,
    CurrentLimitSettings,
    IrDropCompensationSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create linear sweep method parameters.

    Attributes
    ----------
    begin_potential : float
        Begin potential in V (default: -0.5)
    end_potential : float
        End potential in V (default: 0.5)
    step_potential : float
        Step potential in V (default: 0.1)
    scanrate : float
        Scan rate in V/s (default: 1.0)
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False)
        Counter electrode vs ground.
    record_we_potential : bool
        Record applied working electrode potential (default: False)
        Reference electrode vs ground.
    """

    _PSMethod = Techniques.LinearSweep

    begin_potential: float = -0.5
    end_potential: float = 0.5
    step_potential: float = 0.1
    scanrate: float = 1.0

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False
    enable_bipot_current: bool = False

    def update_psobj(self, *, obj):
        """Update method with linear sweep settings."""
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    def update_params(self, *, obj):
        self.begin_potential = obj.BeginPotential
        self.end_potential = obj.EndPotential
        self.step_potential = obj.StepPotential
        self.scanrate = obj.Scanrate

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class SquareWaveParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    PretreatmentSettings,
    VersusOcpSettings,
    BipotSettings,
    PostMeasurementSettings,
    IrDropCompensationSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create square wave method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    begin_potential : float
        Begin potential in V (default: -0.5)
    end_potential : float
        End potential in V (default: 0.5)
    step_potential : float
        Step potential in V (default: 0.1)
    frequency : float
        Frequency in Hz (default: 10.0)
    amplitude : float
        Amplitude in V as half peak-to-peak value (default: 0.05).
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False)
        Counter electrode vs ground.
    record_we_potential : bool
        Record applied working electrode potential (default: False)
        Reference electrode vs ground.
    record_forward_and_reverse_currents : bool
        Record forward and reverse currents (default: False)
    """

    _PSMethod = Techniques.SquareWave

    equilibration_time: float = 0.0
    begin_potential: float = -0.5
    end_potential: float = 0.5
    step_potential: float = 0.1
    frequency: float = 10.0
    amplitude: float = 0.05

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False
    enable_bipot_current: bool = False
    record_forward_and_reverse_currents: bool = False

    def update_psobj(self, *, obj):
        """Update method with linear sweep settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.Frequency = self.frequency
        obj.PulseAmplitude = self.amplitude

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
            record_forward_and_reverse_currents=self.record_forward_and_reverse_currents,
        )

    def update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.begin_potential = obj.BeginPotential
        self.end_potential = obj.EndPotential
        self.step_potential = obj.StepPotential
        self.frequency = obj.Frequency
        self.amplitude = obj.PulseAmplitude

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
            'record_forward_and_reverse_currents',
        ):
            setattr(self, key, msk[key])


@dataclass
class DifferentialPulseParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    PretreatmentSettings,
    VersusOcpSettings,
    BipotSettings,
    PostMeasurementSettings,
    IrDropCompensationSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create square wave method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    begin_potential : float
        Begin potential in V (default: -0.5)
    end_potential : float
        End potential in V (default: 0.5)
    step_potential : float
        Step potential in V (default: 0.1)
    pulse_potential : float
        Pulse potential in V (default: 0.05)
    pulse_time : float
        Pulse time in s (default: 0.01)
    scanrate : float
        Scan rate in V/s (default: 1.0)
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False)
        Counter electrode vs ground.
    record_we_potential : bool
        Record applied working electrode potential (default: False)
        Reference electrode vs ground.
    """

    _PSMethod = Techniques.DifferentialPulse

    equilibration_time: float = 0.0  # Time (s)
    begin_potential: float = -0.5  # potential (V)
    end_potential: float = 0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    pulse_potential: float = 0.05  # potential (V)
    pulse_time: float = 0.01  # time (s)
    scan_rate: float = 1.0  # potential/time (V/s)

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False
    enable_bipot_current: bool = False

    def update_psobj(self, *, obj):
        """Update method with linear sweep settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.PulsePotential = self.pulse_potential
        obj.PulseTime = self.pulse_time
        obj.Scanrate = self.scan_rate

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    def update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.begin_potential = obj.BeginPotential
        self.end_potential = obj.EndPotential
        self.step_potential = obj.StepPotential
        self.pulse_potential = obj.PulsePotential
        self.pulse_time = obj.PulseTime
        self.scan_rate = obj.Scanrate

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class ChronoAmperometryParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    PretreatmentSettings,
    VersusOcpSettings,
    BipotSettings,
    PostMeasurementSettings,
    CurrentLimitSettings,
    ChargeLimitSettings,
    IrDropCompensationSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create chrono amperometry method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    interval_time : float
        Interval time in s (default: 0.1)
    potential : float
        Potential in V (default: 0.0)
    run_time : float
        Run time in s (default: 1.0)
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False)
        Counter electrode vs ground.
    record_we_potential : bool
        Record applied working electrode potential (default: False)
        Reference electrode vs ground.
    """

    _PSMethod = Techniques.AmperometricDetection

    equilibration_time: float = 0.0
    interval_time: float = 0.1
    potential: float = 0.0
    run_time: float = 1.0

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False
    enable_bipot_current: bool = False

    def update_psobj(self, *, obj):
        """Update method with chrono amperometry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time
        obj.Potential = self.potential
        obj.RunTime = self.run_time

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    def update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.interval_time = obj.IntervalTime
        self.potential = obj.Potential
        self.run_time = obj.RunTime

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class MultiStepAmperometryParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    PretreatmentSettings,
    BipotSettings,
    PostMeasurementSettings,
    CurrentLimitSettings,
    IrDropCompensationSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create multi-step amperometry method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    interval_time : float
        Interval time in s (default: 0.1)
    n_cycles : int
        Number of cycles (default: 1)
    levels : list
        List of levels (default: [ELevel()].
        Use ELevel() to create levels.
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False)
        Counter electrode vs ground.
    record_we_potential : bool
        Record applied working electrode potential (default: False)
        Reference electrode vs ground.
    """

    _PSMethod = Techniques.MultistepAmperometry

    equilibration_time: float = 0.0
    interval_time: float = 0.1
    n_cycles: float = 1
    levels: list[ELevel] = field(default_factory=lambda: [ELevel()])

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False
    enable_bipot_current: bool = False

    def update_psobj(self, *, obj):
        """Update method with chrono amperometry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time
        obj.nCycles = self.n_cycles
        obj.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            obj.Levels.Add(level.to_psobj())

        obj.UseSelectiveRecord = any(level.record for level in self.levels)
        obj.UseLimits = any(
            (level.use_limit_current_min or level.use_limit_current_max)
            for level in self.levels
        )

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
            enable_bipot_current=self.enable_bipot_current,
        )

    def update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.interval_time = obj.IntervalTime
        self.n_cycles = obj.nCycles

        self.levels = [ELevel.from_psobj(pslevel) for pslevel in obj.Levels]

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
            'enable_bipot_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class OpenCircuitPotentiometryParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    AutorangingPotentialSettings,
    PretreatmentSettings,
    PostMeasurementSettings,
    PotentialLimitSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create open circuit potentiometry method parameters.

    Attributes
    ----------
    interval_time : float
        Interval time in s (default: 0.1)
    run_time : float
        Run time in s (default: 1.0)
    enable_bipot_current: bool
        Enable bipot current (default: False)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_we_current: bool
        Record working electrode current (default: False)
    record_we_current_range: int
        Record working electrode current range (default: 1 µA)
        Use `get_current_range()` to get the range.
    """

    _PSMethod = Techniques.OpenCircuitPotentiometry

    interval_time: float = 0.1  # Time (s)
    run_time: float = 1.0  # Time (s)

    record_auxiliary_input: bool = False
    record_we_current: bool = False
    record_we_current_range: int = get_current_range(4)

    def update_psobj(self, *, obj):
        """Update method with open circuit potentiometry settings."""
        obj.IntervalTime = self.interval_time
        obj.RunTime = self.run_time
        obj.AppliedCurrentRange = self.record_we_current_range

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    def update_params(self, *, obj):
        self.interval_time = obj.IntervalTime
        self.run_time = obj.RunTime
        self.record_we_current_range = obj.AppliedCurrentRange

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class ChronopotentiometryParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    AutorangingPotentialSettings,
    PretreatmentSettings,
    PostMeasurementSettings,
    PotentialLimitSettings,
    TriggerAtMeasurementSettings,
    FilterSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create potentiometry method parameters.

    Attributes
    ----------
    current : float
        The current to apply. The unit of the value is the applied current range. So if 10 uA is the applied current range and 1.5 is given as value, the applied current will be 15 uA. (default: 0.0)
    applied_current_range : PalmSens.CurrentRange
        Applied current range (default: 100 µA).
        Use `get_current_range()` to get the range.
    interval_time : float
        Interval time in s (default: 0.1)
    run_time : float
        Run time in s (default: 1.0)
    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False) [counter electrode vs ground]
    record_we_current : bool
        Record working electrode current (default: False)
    """

    _PSMethod = Techniques.Potentiometry

    current: float = 0.0
    applied_current_range: int = get_current_range(6)
    interval_time: float = 0.1
    run_time: float = 1.0

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_current: bool = False

    def update_psobj(self, *, obj):
        """Update method with potentiometry settings."""
        obj.Current = self.current
        obj.AppliedCurrentRange = self.applied_current_range
        obj.IntervalTime = self.interval_time
        obj.RunTime = self.run_time

        obj.AppliedCurrentRange = self.applied_current_range

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_current=self.record_we_current,
        )

    def update_params(self, *, obj):
        self.current = obj.Current
        self.applied_current_range = obj.AppliedCurrentRange
        self.interval_time = obj.IntervalTime
        self.run_time = obj.RunTime

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@dataclass
class ElectrochemicalImpedanceSpectroscopyParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    AutorangingPotentialSettings,
    PretreatmentSettings,
    VersusOcpSettings,
    PostMeasurementSettings,
    TriggerAtMeasurementSettings,
    TriggerAtEquilibrationSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create potentiometry method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    dc_potential : float
        DC potential in V (default: 0.0)
    ac_potential : float
        AC potential in V RMS (default: 0.01)
    n_frequencies : int
        Number of frequencies (default: 11)
    max_frequency : float
        Maximum frequency in Hz (default: 1e5)
    min_frequency : float
        Minimum frequency in Hz (default: 1e3)
    """

    _PSMethod = Techniques.ImpedimetricMethod

    equilibration_time: float = 0.0
    dc_potential: float = 0.0
    ac_potential: float = 0.01
    n_frequencies: int = 11
    max_frequency: float = 1e5
    min_frequency: float = 1e3

    def update_psobj(self, *, obj):
        """Update method with potentiometry settings."""
        obj.ScanType = enumScanType.Fixed
        obj.FreqType = enumFrequencyType.Scan
        obj.EquilibrationTime = self.equilibration_time
        obj.Potential = self.dc_potential
        obj.Eac = self.ac_potential
        obj.nFrequencies = self.n_frequencies
        obj.MaxFrequency = self.max_frequency
        obj.MinFrequency = self.min_frequency

    def update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.dc_potential = obj.Potential
        self.ac_potential = obj.Eac
        self.n_frequencies = obj.nFrequencies
        self.max_frequency = obj.MaxFrequency
        self.min_frequency = obj.MinFrequency


@dataclass
class GalvanostaticImpedanceSpectroscopyParameters(
    BaseParameters,
    AutorangingCurrentSettings,
    AutorangingPotentialSettings,
    PretreatmentSettings,
    PostMeasurementSettings,
    TriggerAtEquilibrationSettings,
    TriggerAtMeasurementSettings,
    MultiplexerSettings,
    OtherSettings,
):
    """Create potentiometry method parameters.

    Attributes
    ----------
    applied_current_range : PalmSens.CurrentRange
        Applied current range (default: 100 µA)
        Use `get_current_range()` to get the range.
    ac_current : float
        AC current in applied current range RMS (default: 0.01)
    dc_current : float
        DC current in applied current range (default: 0.0)
    n_frequencies : int
        Number of frequencies (default: 11)
    max_frequency : float
        Maximum frequency in Hz (default: 1e5)
    min_frequency : float
        Minimum frequency in Hz (default: 1e3)
    """

    _PSMethod = Techniques.ImpedimetricGstatMethod

    applied_current_range: float = get_current_range(6)
    equilibration_time: float = 0.0
    ac_current: float = 0.01
    dc_current: float = 0.0
    n_frequencies: int = 11
    max_frequency: float = 1e5
    min_frequency: float = 1e3

    def update_psobj(self, *, obj):
        """Update method with potentiometry settings."""

        obj.ScanType = enumScanType.Fixed
        obj.FreqType = enumFrequencyType.Scan
        obj.AppliedCurrentRange = self.applied_current_range
        obj.EquilibrationTime = self.equilibration_time
        obj.Iac = self.ac_current
        obj.Idc = self.dc_current
        obj.nFrequencies = self.n_frequencies
        obj.MaxFrequency = self.max_frequency
        obj.MinFrequency = self.min_frequency

    def update_params(self, *, obj):
        self.applied_current_range = obj.AppliedCurrentRange
        self.equilibration_time = obj.EquilibrationTime
        self.ac_current = obj.Iac
        self.dc_current = obj.Idc
        self.n_frequencies = obj.nFrequencies
        self.max_frequency = obj.MaxFrequency
        self.min_frequency = obj.MinFrequency
