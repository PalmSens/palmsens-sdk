from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, Protocol, Type, runtime_checkable

import attrs
from PalmSens import Method as PSMethod
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType

from ._shared import (
    CURRENT_RANGE,
    ELevel,
    get_extra_value_mask,
    set_extra_value_mask,
)
from .settings import (
    BiPot,
    ChargeLimits,
    CurrentLimits,
    CurrentRanges,
    DataProcessing,
    EquilibrationTriggers,
    General,
    IrDropCompensation,
    MeasurementTriggers,
    Multiplexer,
    PostMeasurement,
    PotentialLimits,
    PotentialRanges,
    Pretreatment,
    VersusOCP,
)


@runtime_checkable
class MethodSettings(Protocol):
    """Protocol to provide base methods for method classes."""

    __attrs_attrs__: ClassVar[list[attrs.Attribute]] = []
    _id: str

    def _to_psmethod(self) -> PSMethod:
        """Convert parameters to dotnet method."""
        psmethod = PSMethod.FromMethodID(self._id)

        self._update_psmethod(obj=psmethod)

        for field in self.__attrs_attrs__:
            attribute = getattr(self, field.name)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_psmethod(obj=psmethod)
            except AttributeError:
                pass

        return psmethod

    @staticmethod
    def _from_psmethod(psmethod: PSMethod) -> MethodSettings:
        """Generate parameters from dotnet method object."""
        id = psmethod.MethodID

        cls = ID_TO_PARAMETER_MAPPING[id]

        if cls is None:
            raise NotImplementedError(f'Mapping of {id} parameters is not implemented yet')

        new = cls()

        for field in new.__attrs_attrs__:
            attribute = getattr(new, field.name)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_params(obj=psmethod)
            except AttributeError:
                pass

        return new

    @abstractmethod
    def _update_psmethod(self, *, obj: PSMethod) -> None: ...

    @abstractmethod
    def _update_params(self, *, obj: PSMethod) -> None: ...


@attrs.define
class CyclicVoltammetry(MethodSettings):
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

    n_scans: float = 1
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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    current_limits: CurrentLimits = attrs.field(factory=CurrentLimits)
    ir_drop_compensation: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    equilibrion_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
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

    def _update_params(self, *, obj):
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


@attrs.define
class LinearSweepVoltammetry(MethodSettings):
    """Create linear sweep method parameters."""

    _id = 'lsv'

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

    current_ranges: CurrentRanges = CurrentRanges()
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    bipot: BiPot = attrs.field(factory=BiPot)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    current_limits: CurrentLimits = attrs.field(factory=CurrentLimits)
    ir_drop: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    equilibration_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
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

    def _update_params(self, *, obj):
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


@attrs.define
class SquareWaveVoltammetry(MethodSettings):
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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    bipot: BiPot = attrs.field(factory=BiPot)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    ir_drop: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    equilibration_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
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

    def _update_params(self, *, obj):
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


@attrs.define
class DifferentialPulseVoltammetry(MethodSettings):
    """Create square wave method parameters."""

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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    bipot: BiPot = attrs.field(factory=BiPot)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    ir_drop: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    equilibration_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
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

    def _update_params(self, *, obj):
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


@attrs.define
class ChronoAmperometry(MethodSettings):
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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    bipot: BiPot = attrs.field(factory=BiPot)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    current_limits: CurrentLimits = attrs.field(factory=CurrentLimits)
    charge_limits: ChargeLimits = attrs.field(factory=ChargeLimits)
    ir_drop: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    equilibration_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
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

    def _update_params(self, *, obj):
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


@attrs.define
class MultiStepAmperometry(MethodSettings):
    """Create multi-step amperometry method parameters."""

    _id = 'ma'

    equilibration_time: float = 0.0
    """Equilibration time in s."""

    interval_time: float = 0.1
    """Interval time in s."""

    n_cycles: float = 1
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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    bipot: BiPot = attrs.field(factory=BiPot)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    current_limits: CurrentLimits = attrs.field(factory=CurrentLimits)
    ir_drop: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
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

    def _update_params(self, *, obj):
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


@attrs.define
class OpenCircuitPotentiometry(MethodSettings):
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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    potential_ranges: PotentialRanges = attrs.field(factory=PotentialRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    potential_limits: PotentialLimits = attrs.field(factory=PotentialLimits)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
        """Update method with open circuit potentiometry settings."""
        obj.IntervalTime = self.interval_time
        obj.RunTime = self.run_time
        obj.AppliedCurrentRange = self.record_we_current_range._to_psobj()

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    def _update_params(self, *, obj):
        self.interval_time = obj.IntervalTime
        self.run_time = obj.RunTime
        self.record_we_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ChronoPotentiometry(MethodSettings):
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
    """Run time in s (default: 1.0)"""

    record_auxiliary_input: bool = False
    """Record auxiliary input."""

    record_cell_potential: bool = False
    """Record cell potential.

    Counter electrode vs ground."""

    record_we_current: bool = False
    """Record working electrode current."""

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    potential_ranges: PotentialRanges = attrs.field(factory=PotentialRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    potential_limits: PotentialLimits = attrs.field(factory=PotentialLimits)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
        """Update method with potentiometry settings."""
        obj.Current = self.current
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()
        obj.IntervalTime = self.interval_time
        obj.RunTime = self.run_time

        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_current=self.record_we_current,
        )

    def _update_params(self, *, obj):
        self.current = obj.Current
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)
        self.interval_time = obj.IntervalTime
        self.run_time = obj.RunTime

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ElectrochemicalImpedanceSpectroscopy(MethodSettings):
    """Create potentiometry method parameters."""

    _id = 'eis'

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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    potential_ranges: PotentialRanges = attrs.field(factory=PotentialRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    equilibration_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
        """Update method with potentiometry settings."""
        obj.ScanType = enumScanType.Fixed
        obj.FreqType = enumFrequencyType.Scan
        obj.EquilibrationTime = self.equilibration_time
        obj.Potential = self.dc_potential
        obj.Eac = self.ac_potential
        obj.nFrequencies = self.n_frequencies
        obj.MaxFrequency = self.max_frequency
        obj.MinFrequency = self.min_frequency

    def _update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.dc_potential = obj.Potential
        self.ac_potential = obj.Eac
        self.n_frequencies = obj.nFrequencies
        self.max_frequency = obj.MaxFrequency
        self.min_frequency = obj.MinFrequency


@attrs.define
class GalvanostaticImpedanceSpectroscopy(MethodSettings):
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

    current_ranges: CurrentRanges = attrs.field(factory=CurrentRanges)
    potential_ranges: PotentialRanges = attrs.field(factory=PotentialRanges)
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    equilibration_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    general: General = attrs.field(factory=General)

    def _update_psmethod(self, *, obj):
        """Update method with potentiometry settings."""

        obj.ScanType = enumScanType.Fixed
        obj.FreqType = enumFrequencyType.Scan
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()
        obj.EquilibrationTime = self.equilibration_time
        obj.Iac = self.ac_current
        obj.Idc = self.dc_current
        obj.nFrequencies = self.n_frequencies
        obj.MaxFrequency = self.max_frequency
        obj.MinFrequency = self.min_frequency

    def _update_params(self, *, obj):
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)
        self.equilibration_time = obj.EquilibrationTime
        self.ac_current = obj.Iac
        self.dc_current = obj.Idc
        self.n_frequencies = obj.nFrequencies
        self.max_frequency = obj.MaxFrequency
        self.min_frequency = obj.MinFrequency


@attrs.define
class MethodScript(MethodSettings):
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

    def _update_psmethod(self, *, obj):
        """Update method with MethodScript."""
        obj.MethodScript = self.script

    def _update_params(self, *, obj):
        self.script = obj.MethodScript


ID_TO_PARAMETER_MAPPING: dict[str, Type[MethodSettings] | None] = {
    'acv': None,
    'ad': ChronoAmperometry,
    'cc': None,
    'cp': ChronoPotentiometry,
    'cpot': None,
    'cv': CyclicVoltammetry,
    'dpv': DifferentialPulseVoltammetry,
    'eis': ElectrochemicalImpedanceSpectroscopy,
    'fam': None,
    'fcv': None,
    'fgis': None,
    'fis': None,
    'gis': GalvanostaticImpedanceSpectroscopy,
    'gs': None,
    'lp': None,
    'lsp': None,
    'lsv': LinearSweepVoltammetry,
    'ma': MultiStepAmperometry,
    'mm': None,
    'mp': None,
    'mpad': None,
    'ms': MethodScript,
    'npv': None,
    'ocp': OpenCircuitPotentiometry,
    'pad': None,
    'pot': None,
    'ps': None,
    'scp': None,
    'swv': SquareWaveVoltammetry,
}
