from dataclasses import dataclass, field

from PalmSens import Techniques
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType

from ._shared import get_current_range, multi_step_amperometry_level
from .settings import (
    AutorangingCurrentSettings,
    AutorangingPotentialSettings,
    BaseParameters,
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
    """

    # cyclic voltammetry settings
    equilibration_time: float = 0.0  # Time (s)
    begin_potential: float = -0.5  # potential (V)
    vertex1_potential: float = 0.5  # potential (V)
    vertex2_potential: float = -0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    scanrate: float = 1.0  # potential/time (V/s)
    n_scans: float = 1  # number of cycles
    _PSMethod = Techniques.CyclicVoltammetry

    def add_to_object(self, *, obj):
        """Update method with cyclic voltammetry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.Vtx1Potential = self.vertex1_potential
        obj.Vtx2Potential = self.vertex2_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate
        obj.nScans = self.n_scans


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
    """

    # linear sweep voltammetry settings
    begin_potential: float = -0.5  # potential (V)
    end_potential: float = 0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    scanrate: float = 1.0  # potential/time (V/s)
    _PSMethod = Techniques.LinearSweep

    def add_to_object(self, *, obj):
        """Update method with linear sweep settings."""
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate


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
    record_forward_and_reverse_currents : bool
        Record forward and reverse currents (default: False)
    """

    # square wave voltammetry settings
    equilibration_time: float = 0.0
    begin_potential: float = -0.5
    end_potential: float = 0.5
    step_potential: float = 0.1
    frequency: float = 10.0
    amplitude: float = 0.05
    record_forward_and_reverse_currents: bool = False
    _PSMethod = Techniques.SquareWave

    def add_to_object(self, *, obj):
        """Update method with linear sweep settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.Frequency = self.frequency
        obj.PulseAmplitude = self.amplitude

        # if self.record_forward_and_reverse_currents:
        #     extra_values = int(obj.ExtraValueMsk) | int(ExtraValueMask.IForwardReverse)
        #     obj.ExtraValueMsk = ExtraValueMask(extra_values)


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
    """

    # differential pulse voltammetry settings
    equilibration_time: float = 0.0  # Time (s)
    begin_potential: float = -0.5  # potential (V)
    end_potential: float = 0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    pulse_potential: float = 0.05  # potential (V)
    pulse_time: float = 0.01  # time (s)
    scan_rate: float = 1.0  # potential/time (V/s)
    _PSMethod = Techniques.SquareWave

    def add_to_object(self, *, obj):
        """Update method with linear sweep settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.PulsePotential = self.pulse_potential
        obj.PulseTime = self.pulse_time
        obj.Scanrate = self.scan_rate


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
    """

    equilibration_time: float = 0.0
    interval_time: float = 0.1
    potential: float = 0.0
    run_time: float = 1.0
    _PSMethod = Techniques.AmperometricDetection

    def add_to_object(self, *, obj):
        """Update method with chrono amperometry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time
        obj.Potential = self.potential
        obj.RunTime = self.run_time

        # set_extra_value_mask(
        #     dotnet_method,
        #     enable_bipot_current=self.enable_bipot_current,
        #     record_auxiliary_input=self.record_auxiliary_input,
        #     record_cell_potential=self.record_cell_potential,
        #     record_we_potential=self.record_we_potential,
        # )


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
        List of levels (default: [multi_step_amperometry_level()].
        Use multi_step_amperometry_level() to create levels.
    """

    equilibration_time: float = 0.0  # Time (s)
    interval_time: float = 0.1  # Time (s)
    n_cycles: float = 1  # Number of cycles
    levels: list[Techniques.ELevel] = field(
        default_factory=lambda: [multi_step_amperometry_level()]
    )
    _PSMethod = Techniques.MultistepAmperometry

    def add_to_object(self, *, obj):
        """Update method with chrono amperometry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time
        obj.nCycles = self.n_cycles
        obj.Levels.Clear()

        if len(self.levels) == 0:
            raise ValueError('At least one level must be specified.')

        use_partial_record = False
        use_level_limits = False

        for level in self.levels:
            if level.Record:
                use_partial_record = True
            if level.UseMaxLimit or level.UseMinLimit:
                use_level_limits = True

            obj.Levels.Add(level)

        obj.UseSelectiveRecord = use_partial_record
        obj.UseLimits = use_level_limits


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
    record_we_current_range: int
        Record working electrode current range (default: 1 µA)
        Use `get_current_range()` to get the range.
    """

    interval_time: float = 0.1  # Time (s)
    run_time: float = 1.0  # Time (s)

    # record extra value settings
    record_we_current_range: int = get_current_range(4)

    _PSMethod = Techniques.OpenCircuitPotentiometry

    def add_to_object(self, *, obj):
        """Update method with open circuit potentiometry settings."""

        obj.IntervalTime = self.interval_time
        obj.RunTime = self.run_time

        # set_extra_value_mask(
        #     dotnet_method,
        #     record_auxiliary_input=self.record_auxiliary_input,
        #     record_cell_potential=self.record_cell_potential,
        #     record_we_current=self.record_we_current,
        #     record_we_current_range=self.record_we_current_range,
        # )


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
        Current in applied current range (default: 0.0)
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
    record_we_current_range: int=get_potential_range(4)
        Record working electrode current range (default: 1 µA)
        Use `get_current_range()` to get the range.
    """

    current: float = 0.0  # in applied current range
    applied_current_range: int = get_current_range(6)  # in applied current range
    interval_time: float = 0.1  # Time (s)
    run_time: float = 1.0  # Time (s)

    _PSMethod = Techniques.Potentiometry

    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_current: bool = False
    record_we_current_range: int = get_current_range(4)

    def add_to_object(self, *, obj):
        """Update method with potentiometry settings."""
        obj.Current = self.current
        obj.AppliedCurrentRange = self.applied_current_range
        obj.IntervalTime = self.interval_time
        obj.RunTime = self.run_time

        # set_extra_value_mask(
        #     obj,
        #     record_auxiliary_input=self.record_auxiliary_input,
        #     record_cell_potential=self.record_cell_potential,
        #     record_we_current=self.record_we_current,
        #     record_we_current_range=self.applied_current_range,
        # )


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

    equilibration_time: float = 0.0  # Time (s)
    dc_potential: float = 0.0  # in V
    ac_potential: float = 0.01  # in V RMS
    n_frequencies: float = 11  # Number of frequencies
    max_frequency: float = 1e5  # in Hz
    min_frequency: float = 1e3  # in Hz

    _PSMethod = Techniques.ImpedimetricMethod

    def add_to_object(self, *, obj):
        """Update method with potentiometry settings."""

        obj.ScanType = enumScanType.Fixed
        obj.FreqType = enumFrequencyType.Scan
        obj.EquilibrationTime = self.equilibration_time
        obj.Potential = self.dc_potential
        obj.Eac = self.ac_potential
        obj.nFrequencies = self.n_frequencies
        obj.MaxFrequency = self.max_frequency
        obj.MinFrequency = self.min_frequency


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

    applied_current_range: float = get_current_range(6)  # in applied current range
    equilibration_time: float = 0.0  # Time (s
    ac_current: float = 0.01  # in applied current range RMS
    dc_current: float = 0.0  # in applied current range
    n_frequencies: int = 11  # Number of frequencies
    max_frequency: float = 1e5  # in Hz
    min_frequency: float = 1e3  # in Hz

    _PSMethod = Techniques.ImpedimetricGstatMethod

    def add_to_object(self, *, obj):
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
