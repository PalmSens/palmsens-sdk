from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, Literal, Protocol, Type, runtime_checkable

import attrs
import PalmSens.Techniques as PSTechniques
from PalmSens import FixedCurrentRange as PSFixedCurrentRange
from PalmSens import Method as PSMethod
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType

from ._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    ELevel,
    ILevel,
    get_extra_value_mask,
    set_extra_value_mask,
)
from .settings import (
    BiPot,
    ChargeLimits,
    CurrentLimits,
    CurrentRange,
    DataProcessing,
    DelayTriggers,
    EquilibrationTriggers,
    General,
    IrDropCompensation,
    MeasurementTriggers,
    Multiplexer,
    PostMeasurement,
    PotentialLimits,
    PotentialRange,
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


def current_converter(value: CURRENT_RANGE | CurrentRange) -> CurrentRange:
    if isinstance(value, CURRENT_RANGE):
        return CurrentRange(min=value, max=value, start=value)
    return value


@attrs.define(slots=False)
class CurrentRangeMixin:
    current_range: CurrentRange = attrs.field(factory=CurrentRange, converter=current_converter)
    """Set the autoranging current."""


def potential_converter(value: POTENTIAL_RANGE | PotentialRange) -> PotentialRange:
    if isinstance(value, POTENTIAL_RANGE):
        return PotentialRange(min=value, max=value, start=value)
    return value


@attrs.define(slots=False)
class PotentialRangeMixin:
    potential_range: PotentialRange = attrs.field(
        factory=PotentialRange, converter=potential_converter
    )
    """Set the autoranging potential."""


@attrs.define(slots=False)
class PretreatmentMixin:
    pretreatment: Pretreatment = attrs.field(factory=Pretreatment)
    """Set the pretreatment settings."""


@attrs.define(slots=False)
class VersusOCPMixin:
    versus_ocp: VersusOCP = attrs.field(factory=VersusOCP)
    """Set the versus OCP settings."""


@attrs.define(slots=False)
class BiPotMixin:
    bipot: BiPot = attrs.field(factory=BiPot)
    """Set the bipot settings"""


@attrs.define(slots=False)
class PostMeasurementMixin:
    post_measurement: PostMeasurement = attrs.field(factory=PostMeasurement)
    """Set the post measurement settings."""


@attrs.define(slots=False)
class CurrentLimitsMixin:
    current_limits: CurrentLimits = attrs.field(factory=CurrentLimits)
    """Set the current limit settings."""


@attrs.define(slots=False)
class PotentialLimitsMixin:
    potential_limits: PotentialLimits = attrs.field(factory=PotentialLimits)
    """Set the potential limit settings"""


@attrs.define(slots=False)
class ChargeLimitsMixin:
    charge_limits: ChargeLimits = attrs.field(factory=ChargeLimits)
    """Set the charge limit settings"""


@attrs.define(slots=False)
class IrDropCompensationMixin:
    ir_drop_compensation: IrDropCompensation = attrs.field(factory=IrDropCompensation)
    """Set the iR drop compensation settings."""


@attrs.define(slots=False)
class EquilibrationTriggersMixin:
    equilibrion_triggers: EquilibrationTriggers = attrs.field(factory=EquilibrationTriggers)
    """Set the trigger at equilibration settings."""


@attrs.define(slots=False)
class MeasurementTriggersMixin:
    measurement_triggers: MeasurementTriggers = attrs.field(factory=MeasurementTriggers)
    """Set the trigger at measurement settings."""


@attrs.define(slots=False)
class DelayTriggersMixin:
    delay_triggers: DelayTriggers = attrs.field(factory=DelayTriggers)
    """Set the delayed trigger at measurement settings."""


@attrs.define(slots=False)
class MultiplexerMixin:
    multiplexer: Multiplexer = attrs.field(factory=Multiplexer)
    """Set the multiplexer settings"""


@attrs.define(slots=False)
class DataProcessingMixin:
    data_processing: DataProcessing = attrs.field(factory=DataProcessing)
    """Set the data processing settings."""


@attrs.define(slots=False)
class GeneralMixin:
    general: General = attrs.field(factory=General)
    """Sets general/other settings."""


@attrs.define
class CyclicVoltammetry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    PostMeasurementMixin,
    CurrentLimitsMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with fast cyclic voltammetry settings."""
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
class FastCyclicVoltammetry(
    MethodSettings,
    PretreatmentMixin,
    VersusOCPMixin,
    PostMeasurementMixin,
    IrDropCompensationMixin,
    DataProcessingMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with fast cyclic voltammetry settings."""

        obj.Ranging = PSFixedCurrentRange(self.current_range._to_psobj())
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.Vtx1Potential = self.vertex1_potential
        obj.Vtx2Potential = self.vertex2_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate
        obj.nScans = self.n_scans
        obj.nAvgScans = self.n_avg_scans
        obj.nEqScans = self.n_equil_scans

    def _update_params(self, *, obj):
        self.current_range = CURRENT_RANGE._from_psobj(obj.Ranging.StartCurrentRange)
        self.equilibration_time = obj.EquilibrationTime
        self.begin_potential = obj.BeginPotential
        self.vertex1_potential = obj.Vtx1Potential
        self.vertex2_potential = obj.Vtx2Potential
        self.step_potential = obj.StepPotential
        self.scanrate = obj.Scanrate
        self.n_scans = obj.nScans
        self.n_avg_scans = obj.nAvgScans
        self.n_equil_scans = obj.nEqScans


@attrs.define
class ACVoltammetry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    PostMeasurementMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with linear sweep settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
        obj.Frequency = self.frequency
        obj.SineWaveAmplitude = self.ac_potential
        obj.MeasureDCcurrent = self.measure_dc_current
        obj.Scanrate = self.scanrate

    def _update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.begin_potential = obj.BeginPotential
        self.end_potential = obj.EndPotential
        self.step_potential = obj.StepPotential
        self.ac_potential = obj.SineWaveAmplitude
        self.frequency = obj.Frequency
        self.scanrate = obj.Scanrate
        self.measure_dc_current = obj.MeasureDCcurrent


@attrs.define
class LinearSweepVoltammetry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    CurrentLimitsMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with linear sweep settings."""
        obj.EquilibrationTime = self.equilibration_time
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
        self.equilibration_time = obj.EquilibrationTime
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
class SquareWaveVoltammetry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with square wave voltammetry settings."""
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
class DifferentialPulseVoltammetry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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
class NormalPulseVoltammetry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with normal pulse voltammetry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.BeginPotential = self.begin_potential
        obj.EndPotential = self.end_potential
        obj.StepPotential = self.step_potential
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
class ChronoAmperometry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    CurrentLimitsMixin,
    ChargeLimitsMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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
class FastAmperometry(
    MethodSettings,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    CurrentLimitsMixin,
    ChargeLimitsMixin,
    IrDropCompensationMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with fast amperometry settings."""
        obj.Ranging = PSFixedCurrentRange(self.current_range._to_psobj())
        obj.EquilibrationTime = self.equilibration_time
        obj.EqPotentialFA = self.equilibration_potential
        obj.IntervalTime = self.interval_time
        obj.Potential = self.potential
        obj.RunTime = self.run_time

    def _update_params(self, *, obj):
        self.current_range = CURRENT_RANGE._from_psobj(obj.Ranging.StartCurrentRange)
        self.equilibration_time = obj.EquilibrationTime
        self.equilibration_potential = obj.EqPotentialFA
        self.interval_time = obj.IntervalTime
        self.potential = obj.Potential
        self.run_time = obj.RunTime


@attrs.define
class MultiStepAmperometry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    BiPotMixin,
    PostMeasurementMixin,
    CurrentLimitsMixin,
    IrDropCompensationMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
):
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

    def _update_psmethod(self, *, obj):
        """Update method with multistep amperometry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time
        obj.nCycles = self.n_cycles
        obj.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            obj.Levels.Add(level.to_psobj())

        obj.UseSelectiveRecord = any(level.record for level in self.levels)
        obj.UseLimits = any(level.use_limits for level in self.levels)

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
class PulsedAmperometricDetection(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    BiPotMixin,
    PostMeasurementMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    DelayTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
):
    """Create pulsed amperometric detection method parameters."""

    _id = 'pad'

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

    _MODES = ('dc', 'pulse', 'differential')

    def _update_psmethod(self, *, obj):
        """Update method with pulsed amperometric detection settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time
        obj.PulseTime = self.pulse_time
        obj.PulsePotential = self.pulse_potential
        obj.Potential = self.potential
        obj.RunTime = self.run_time

        mode = self._MODES.index(self.mode) + 1
        obj.tMode = PSTechniques.PulsedAmpDetection.enumMode(mode)

    def _update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.interval_time = obj.IntervalTime
        self.potential = obj.Potential
        self.pulse_potential = obj.PulsePotential
        self.pulse_time = obj.PulseTime
        self.run_time = obj.RunTime

        self.mode = self._MODES[int(obj.tMode) - 1]


@attrs.define
class OpenCircuitPotentiometry(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    PotentialLimitsMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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
class ChronoPotentiometry(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    PotentialLimitsMixin,
    MeasurementTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with chronopotentiometry settings."""
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
class StrippingChronoPotentiometry(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    DataProcessingMixin,
    GeneralMixin,
):
    """Create stripping potentiometry method parameters.

    If the stripping current is set to 0, then chemical stripping is performed,
    otherwise it is chemical constant current stripping.
    The applicable range is +- 0.001 microampere to +- 2 milliampere.
    """

    _id = 'scp'

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
    """Measurement time in s (default: 1.0)"""

    def _update_psmethod(self, *, obj):
        """Update method with stripping chrono potentiometry settings."""
        obj.Current = self.current
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()
        obj.MeasurementTime = self.measurement_time
        obj.EndPotential = self.end_potential

        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()

    def _update_params(self, *, obj):
        self.current = obj.Current
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)
        self.measurement_time = obj.MeasurementTime
        self.end_potential = obj.EndPotential


@attrs.define
class LinearSweepPotentiometry(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    PotentialLimitsMixin,
    MeasurementTriggersMixin,
    DelayTriggersMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with lineas sweep potentiometry settings."""
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()

        obj.BeginCurrent = self.current_begin
        obj.EndCurrent = self.current_end
        obj.StepCurrent = self.current_step
        obj.ScanrateG = self.scan_rate

        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    def _update_params(self, *, obj):
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)

        self.current_begin = obj.BeginCurrent
        self.current_end = obj.EndCurrent
        self.current_step = obj.StepCurrent
        self.scan_rate = obj.ScanrateG

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class MultiStepPotentiometry(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    PotentialLimitsMixin,
    DataProcessingMixin,
    MultiplexerMixin,
    GeneralMixin,
):
    """Create multi-step potentiometry method parameters."""

    _id = 'mp'

    applied_current_range: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    """Applied current range.

    Use `CURRENT_RANGE` to define the range."""

    interval_time: float = 0.1
    """Interval time in s."""

    n_cycles: float = 1
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

    def _update_psmethod(self, *, obj):
        """Update method with multistep potentiometry settings."""
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()
        obj.IntervalTime = self.interval_time
        obj.nCycles = self.n_cycles
        obj.Levels.Clear()

        if not self.levels:
            raise ValueError('At least one level must be specified.')

        for level in self.levels:
            obj.Levels.Add(level.to_psobj())

        obj.UseSelectiveRecord = any(level.record for level in self.levels)
        obj.UseLimits = any(level.use_limits for level in self.levels)

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_we_current=self.record_we_current,
        )

    def _update_params(self, *, obj):
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)

        self.interval_time = obj.IntervalTime
        self.n_cycles = obj.nCycles

        self.levels = [ILevel.from_psobj(pslevel) for pslevel in obj.Levels]

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_we_current',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ChronoCoulometry(
    MethodSettings,
    CurrentRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    CurrentLimitsMixin,
    ChargeLimitsMixin,
    DataProcessingMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with chrono coulometry settings."""
        obj.EquilibrationTime = self.equilibration_time
        obj.IntervalTime = self.interval_time

        obj.EFirstStep = self.step1_potential
        obj.ESecondStep = self.step2_potential
        obj.TFirstStep = self.step1_run_time
        obj.TSecondStep = self.step2_run_time

        if self.bandwidth is not None:
            obj.OverrideBandwidth = True
            obj.Bandwidth = self.bandwidth

        set_extra_value_mask(
            obj=obj,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
        )

    def _update_params(self, *, obj):
        self.equilibration_time = obj.EquilibrationTime
        self.interval_time = obj.IntervalTime
        self.step1_potential = obj.EFirstStep
        self.step2_potential = obj.ESecondStep
        self.step1_run_time = obj.TFirstStep
        self.step2_run_time = obj.TSecondStep

        if obj.OverrideBandwidth:
            self.bandwidth = obj.Bandwidth

        msk = get_extra_value_mask(obj)

        for key in (
            'record_auxiliary_input',
            'record_cell_potential',
            'record_we_potential',
        ):
            setattr(self, key, msk[key])


@attrs.define
class ElectrochemicalImpedanceSpectroscopy(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    PostMeasurementMixin,
    MeasurementTriggersMixin,
    EquilibrationTriggersMixin,
    MultiplexerMixin,
    GeneralMixin,
):
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

    def _update_psmethod(self, *, obj):
        """Update method with electrochemical impedance spectroscopy settings."""
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
class FastImpedanceSpectroscopy(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    VersusOCPMixin,
    PostMeasurementMixin,
    MeasurementTriggersMixin,
    EquilibrationTriggersMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with fas impedance spectroscopy settings."""
        obj.Eac = self.ac_potential
        obj.EquilibrationTime = self.equilibration_time
        obj.FixedFrequency = self.frequency
        obj.IntervalTime = self.interval_time
        obj.Potential = self.dc_potential
        obj.RunTime = self.run_time

    def _update_params(self, *, obj):
        self.ac_potential = obj.Eac
        self.equilibration_time = obj.EquilibrationTime
        self.frequency = obj.FixedFrequency
        self.interval_time = obj.IntervalTime
        self.dc_potential = obj.Potential
        self.run_time = obj.RunTime


@attrs.define
class GalvanostaticImpedanceSpectroscopy(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    EquilibrationTriggersMixin,
    MeasurementTriggersMixin,
    MultiplexerMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with galvanic impedance spectroscopy settings."""

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
class FastGalvanostaticImpedanceSpectroscopy(
    MethodSettings,
    CurrentRangeMixin,
    PotentialRangeMixin,
    PretreatmentMixin,
    PostMeasurementMixin,
    GeneralMixin,
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

    def _update_psmethod(self, *, obj):
        """Update method with fast galvanic impedance spectroscopy settings."""
        obj.AppliedCurrentRange = self.applied_current_range._to_psobj()
        obj.Iac = self.ac_current
        obj.Idc = self.dc_current
        obj.FixedFrequency = self.frequency
        obj.RunTime = self.run_time
        obj.IntervalTime = self.interval_time

    def _update_params(self, *, obj):
        self.applied_current_range = CURRENT_RANGE._from_psobj(obj.AppliedCurrentRange)
        self.ac_current = obj.Iac
        self.dc_current = obj.Idc
        self.frequency = obj.FixedFrequency
        self.run_time = obj.RunTime
        self.interval_time = obj.IntervalTime


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
    'acv': ACVoltammetry,
    'ad': ChronoAmperometry,
    'cc': ChronoCoulometry,
    'cp': None,  # CyclicPolarization
    'cpot': None,  # CorrosionPotential
    'cv': CyclicVoltammetry,
    'dpv': DifferentialPulseVoltammetry,
    'eis': ElectrochemicalImpedanceSpectroscopy,
    'fam': FastAmperometry,
    'fcv': FastCyclicVoltammetry,
    'fgis': FastGalvanostaticImpedanceSpectroscopy,
    'fis': FastImpedanceSpectroscopy,
    'gis': GalvanostaticImpedanceSpectroscopy,
    'gs': None,  # Galvanostatic
    'lp': None,  # LinearPolarization
    'lsp': LinearSweepPotentiometry,
    'lsv': LinearSweepVoltammetry,
    'ma': MultiStepAmperometry,
    'mm': None,  # MixedMode
    'mp': MultiStepPotentiometry,
    'mpad': None,  # MultiplePulseAmperometry
    'ms': MethodScript,
    'npv': NormalPulseVoltammetry,
    'ocp': OpenCircuitPotentiometry,
    'pad': PulsedAmperometricDetection,
    'pot': ChronoPotentiometry,
    'ps': None,  # Potentiostatic
    'scp': StrippingChronoPotentiometry,
    'swv': SquareWaveVoltammetry,
}
