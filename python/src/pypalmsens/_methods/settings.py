from __future__ import annotations

from functools import reduce
from operator import ior
from typing import Literal

import PalmSens
from pydantic import Field, field_validator
from typing_extensions import override

from .._converters import (
    cr_enum_to_string,
    cr_string_to_enum,
    pr_enum_to_string,
    pr_string_to_enum,
    single_to_double,
)
from .._types import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
    OCPFlag,
)
from .base import BaseSettings
from .base_model import BaseModel
from .levels import (
    convert_bools_to_int,
    convert_int_to_bools,
)


class CurrentRange(BaseSettings):
    """Set the autoranging current.

    Examples
    --------
    As a `CurrentRange` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import CurrentRange
    >>> method = ps.CyclicVoltammetry(
    ...     current_range=CurrentRange(
    ...         min='1uA',
    ...         max='10mA',
    ...         start='100uA',
    ...     ),
    ... )

    From a dict (coerced to a `CurrentRange` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     current_range={
    ...         'min': '1uA',
    ...         'max': '10mA',
    ...         'start': '100uA',
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.current_range.min = '1uA'
    >>> method.current_range.max = '10mA'
    >>> method.current_range.start = '100uA'
    """

    min: AllowedCurrentRanges = '1uA'
    """Minimum current range.

    See [pypalmsens.types.AllowedCurrentRanges][] for options."""

    max: AllowedCurrentRanges = '10mA'
    """Maximum current range.

    See [pypalmsens.types.AllowedCurrentRanges][] for options."""

    start: AllowedCurrentRanges = '100uA'
    """Start current range.

    See [pypalmsens.types.AllowedCurrentRanges][] for options."""

    @override
    def _export(self, psmethod: PalmSens.Method, /, bipot: bool = False):
        obj = psmethod.BipotRanging if bipot else psmethod.Ranging

        obj.MaximumCurrentRange = cr_string_to_enum(self.max)
        obj.MinimumCurrentRange = cr_string_to_enum(self.min)
        obj.StartCurrentRange = cr_string_to_enum(self.start)

    @override
    def _import(self, psmethod: PalmSens.Method, /, bipot: bool = False):
        obj = psmethod.BipotRanging if bipot else psmethod.Ranging

        self.max = cr_enum_to_string(obj.MaximumCurrentRange)
        self.min = cr_enum_to_string(obj.MinimumCurrentRange)
        self.start = cr_enum_to_string(obj.StartCurrentRange)


class PotentialRange(BaseSettings):
    """Set the autoranging potential.

    Examples
    --------
    As a `PotentialRange` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import PotentialRange
    >>> method = ps.ChronoPotentiometry(
    ...     potential_range=PotentialRange(
    ...         min='1mV',
    ...         max='1V',
    ...         start='1V',
    ...     ),
    ... )

    From a dict (coerced to a `PotentialRange` by Pydantic):

    >>> method = ps.ChronoPotentiometry(
    ...     potential_range={
    ...         'min': '1mV',
    ...         'max': '1V',
    ...         'start': '1V',
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.ChronoPotentiometry()
    >>> method.potential_range.min = '1mV'
    >>> method.potential_range.max = '1V'
    >>> method.potential_range.start = '1V'
    """

    min: AllowedPotentialRanges = '1mV'
    """Minimum potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    max: AllowedPotentialRanges = '1V'
    """Maximum potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    start: AllowedPotentialRanges = '1V'
    """Start potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.RangingPotential.MaximumPotentialRange = pr_string_to_enum(self.max)
        psmethod.RangingPotential.MinimumPotentialRange = pr_string_to_enum(self.min)
        psmethod.RangingPotential.StartPotentialRange = pr_string_to_enum(self.start)

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.max = pr_enum_to_string(psmethod.RangingPotential.MaximumPotentialRange)
        self.min = pr_enum_to_string(psmethod.RangingPotential.MinimumPotentialRange)
        self.start = pr_enum_to_string(psmethod.RangingPotential.StartPotentialRange)


class Pretreatment(BaseSettings):
    """Set the measurement pretreatment settings.

    Examples
    --------
    As a `Pretreatment` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import Pretreatment
    >>> method = ps.CyclicVoltammetry(
    ...     pretreatment=Pretreatment(
    ...         deposition_potential=1.0,
    ...         deposition_time=5.0,
    ...         conditioning_potential=1.0,
    ...         conditioning_time=5.0,
    ...     ),
    ... )

    From a dict (coerced to a `Pretreatment` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     pretreatment={
    ...         'deposition_potential': 1.0,
    ...         'deposition_time': 5.0,
    ...         'conditioning_potential': 1.0,
    ...         'conditioning_time': 5.0,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.pretreatment.deposition_potential = 1.0
    >>> method.pretreatment.deposition_time = 5.0
    >>> method.pretreatment.conditioning_potential = 1.0
    >>> method.pretreatment.conditioning_time = 5.0
    """

    deposition_potential: float = 0.0
    """Deposition potential in V."""

    deposition_time: float = 0.0
    """Deposition time in s."""

    conditioning_potential: float = 0.0
    """Conditioning potential in V."""

    conditioning_time: float = 0.0
    """Conditioning time in s."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.DepositionPotential = self.deposition_potential
        psmethod.DepositionTime = self.deposition_time
        psmethod.ConditioningPotential = self.conditioning_potential
        psmethod.ConditioningTime = self.conditioning_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.deposition_potential = single_to_double(psmethod.DepositionPotential)
        self.deposition_time = single_to_double(psmethod.DepositionTime)
        self.conditioning_potential = single_to_double(psmethod.ConditioningPotential)
        self.conditioning_time = single_to_double(psmethod.ConditioningTime)


class VersusOCP(BaseSettings):
    """Define which potentials to measure versus Open Circuit Potential (OCP).

    Usually, potentials refer to the Working Electrode (WE) relative
    to the Reference Electrode (RE).
    Use this class to define which potentials (`potentials`) are relative
    to the OCP.

    To do so, the technique determines the stable OCP value first.
    This requires measuring the OCP drift until it settles (`stability_criterion`)
    or times out (`timeout`) before starting with the measurement.

    The following potentials can be defined relative to OCP:

    - `'vertex1'`, `'vertex2'`: Potential at which the scan direction is reversed
    - `'begin'`: Potential applied at the beginning of a measurement
    - `'end'`: Potential applied at the end of a measurement
    - `'potential'`: Potential applied during measurement

    Examples
    --------
    As a `VersusOCP` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import VersusOCP
    >>> method = ps.CyclicVoltammetry(
    ...     versus_ocp=VersusOCP(
    ...         potentials=['begin', 'end'],
    ...         timeout=20.0,
    ...         stability_criterion=0.0,
    ...     ),
    ... )

    From a dict (coerced to a `VersusOCP` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     versus_ocp={
    ...         'potentials': ['begin', 'end'],
    ...         'timeout': 20.0,
    ...         'stability_criterion': 0.0,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.versus_ocp.potentials = ['begin', 'end']
    >>> method.versus_ocp.timeout = 20.0
    >>> method.versus_ocp.stability_criterion = 0.0
    """

    potentials: list[OCPFlag] = Field(default_factory=list, strict=False)
    """Define these potentials vs OCP.

    Different methods use different values:

    - CV, FCV, CP: `'vertex1'`, `'vertex2'`, `'begin'`
    - EIS, FIS: `'begin'`, `'end'`
    - EIS (potential scan): `'potential'`
    - AD, PS, FAM: `'potential`'
    - LSV, ACV, LP, SWV, DPV, NPV: `'begin'`, `'end'`

    Leave blank to disable versus OCP measurements.
    """

    timeout: float = 20.0
    """Maximum time in s to determine OCP value.

    Set the OCP value when the `timeout` has elapsed.
    """

    stability_criterion: float = 0.0
    """Stability criterion (potential/time) in mV/s.

    Set the OCP value when the drift is lower than the specified value.

    If equal to 0 means no stability criterion.
    If larger than 0, then the value is taken as the stability threshold.
    """

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        ocp_flag_map = self._ocp_flag_map(psmethod)

        if self.potentials:
            mode = reduce(ior, [ocp_flag_map[key] for key in self.potentials])
        else:
            mode = 0

        psmethod.OCPmode = mode
        psmethod.OCPMaxOCPTime = self.timeout
        psmethod.OCPStabilityCriterion = self.stability_criterion

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        ocp_flag_map = self._ocp_flag_map(psmethod)

        if mode := psmethod.OCPmode:
            potentials = [key for key, val in ocp_flag_map.items() if (mode & val) == val]
        else:
            potentials = []

        self.potentials = potentials  # type: ignore
        self.timeout = single_to_double(psmethod.OCPMaxOCPTime)
        self.stability_criterion = single_to_double(psmethod.OCPStabilityCriterion)

    def _ocp_flag_map(self, psmethod: PalmSens.Method) -> dict[str, int]:
        method_id = psmethod.MethodID

        if method_id in ('cv', 'fcv', 'cp'):
            return {'vertex1': 1, 'vertex2': 2, 'begin': 4}
        elif method_id in ('eis', 'fis'):
            if str(psmethod.ScanType) == 'PGScan':
                return {'begin': 1, 'end': 2}
            else:
                return {'potential': 1}
        elif method_id in ('ad', 'ps', 'fam'):
            return {'potential': 1}
        elif method_id in ('lsv', 'acv', 'lp', 'swv', 'dpv', 'npv'):
            return {'begin': 1, 'end': 2}

        raise TypeError(f'{method_id} does not support OCP.')


class BiPot(BaseSettings):
    """Set the bipot settings.

    Examples
    --------
    As a `BiPot` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import BiPot
    >>> method = ps.CyclicVoltammetry(
    ...     bipot=BiPot(
    ...         mode='constant',
    ...         potential=1.0,
    ...     ),
    ... )

    From a dict (coerced to a `BiPot` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     bipot={
    ...         'mode': 'constant',
    ...         'potential': 1.0,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.bipot.mode = 'constant'
    >>> method.bipot.potential = 1.0
    """

    _MODES: tuple[Literal['constant', 'offset'], ...] = ('constant', 'offset')

    mode: Literal['constant', 'offset'] = 'constant'
    """Set the bipotential mode.

    Possible values: `constant` or `offset`"""

    potential: float = 0.0
    """Set the bipotential in V."""

    current_range: CurrentRange = Field(default_factory=CurrentRange)
    """Set the bipotential current range.

    Can be a fixed current range or a ranging current. See the specifications for your instrument.
    Internally, a fixed current range is represented by an autoranging current with equal min/max ranges.

    See [pypalmsens.types.AllowedCurrentRanges][] for options."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        bipot_num = self._MODES.index(self.mode)
        psmethod.BipotModePS = PalmSens.Method.EnumPalmSensBipotMode(bipot_num)
        psmethod.BiPotPotential = self.potential

        self.current_range._export(psmethod, bipot=True)

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.mode = self._MODES[int(psmethod.BipotModePS)]
        self.potential = single_to_double(psmethod.BiPotPotential)

        self.current_range._import(psmethod, bipot=True)

    @field_validator('current_range', mode='before')
    @classmethod
    def current_converter(cls, value: AllowedCurrentRanges | CurrentRange) -> CurrentRange:
        if isinstance(value, str):
            return CurrentRange(min=value, max=value, start=value)
        return value


class PostMeasurement(BaseSettings):
    """Set the post measurement settings.
    Examples
    --------
    As a `PostMeasurement` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import PostMeasurement
    >>> method = ps.CyclicVoltammetry(
    ...     post_measurement=PostMeasurement(
    ...         cell_on_after_measurement=True,
    ...         standby_potential=1.0,
    ...         standby_time=5.0,
    ...     ),
    ... )

    From a dict (coerced to a `PostMeasurement` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     post_measurement={
    ...         'cell_on_after_measurement': True,
    ...         'standby_potential': 1.0,
    ...         'standby_time': 5.0,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.post_measurement.cell_on_after_measurement = True
    >>> method.post_measurement.standby_potential = 1.0
    >>> method.post_measurement.standby_time = 5.0
    """

    cell_on_after_measurement: bool = False
    """Enable/disable cell after measurement."""

    standby_potential: float = 0.0
    """Standby potential (V) for use with cell on after measurement."""

    standby_time: float = 0.0
    """Standby time (s) for use with cell on after measurement."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.CellOnAfterMeasurement = self.cell_on_after_measurement
        psmethod.StandbyPotential = self.standby_potential
        psmethod.StandbyTime = self.standby_time

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.cell_on_after_measurement = psmethod.CellOnAfterMeasurement
        self.standby_potential = single_to_double(psmethod.StandbyPotential)
        self.standby_time = single_to_double(psmethod.StandbyTime)


class CurrentLimits(BaseSettings):
    """Adjust the current limits.

    Depending on the method, this will:

    - Abort the measurement
    - Reverse the scan instead (CV)
    - Proceed to the next stage (Mixed Mode)

    Examples
    --------
    As a `CurrentLimits` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import CurrentLimits
    >>> method = ps.CyclicVoltammetry(
    ...     current_limits=CurrentLimits(
    ...         max=0.10,
    ...         min=0.01,
    ...     ),
    ... )

    From a dict (coerced to a `CurrentLimits` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     current_limits={
    ...         'max': 0.10,
    ...         'min': 0.01,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.current_limits.max = 0.10
    >>> method.current_limits.min = 0.01
    """

    min: None | float = None
    """Set current limit min in µA.

    `None` disables the limit."""

    max: None | float = None
    """Set current limit max in µA.

    `None` disables the limit."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        if self.max is not None:
            psmethod.UseLimitMaxValue = True
            psmethod.LimitMaxValue = self.max
        else:
            psmethod.UseLimitMaxValue = False

        if self.min is not None:
            psmethod.UseLimitMinValue = True
            psmethod.LimitMinValue = self.min
        else:
            psmethod.UseLimitMinValue = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        if psmethod.UseLimitMaxValue:
            self.max = single_to_double(psmethod.LimitMaxValue)
        else:
            self.max = None

        if psmethod.UseLimitMinValue:
            self.min = single_to_double(psmethod.LimitMinValue)
        else:
            self.min = None


class PotentialLimits(BaseSettings):
    """Adjust the potential limits.

    Depending on the method, this will:

    - Abort the measurement
    - Proceed to the next stage (Mixed Mode)

    Examples
    --------
    As a `PotentialLimits` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import PotentialLimits
    >>> method = ps.ChronoPotentiometry(
    ...     potential_limits=PotentialLimits(
    ...         min=-0.5,
    ...         max=0.5,
    ...     ),
    ... )

    From a dict (coerced to a `PotentialLimits` by Pydantic):

    >>> method = ps.ChronoPotentiometry(
    ...     potential_limits={
    ...         'min': -0.5,
    ...         'max': 0.5,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.ChronoPotentiometry()
    >>> method.potential_limits.min = -0.5
    >>> method.potential_limits.max = 0.5
    """

    min: None | float = None
    """Set potential limit min in V.

    `None` disables the limit."""

    max: None | float = None
    """Set potential limit max in V.

    `None` disables the limit."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        if self.max is not None:
            psmethod.UseLimitMaxValue = True
            psmethod.LimitMaxValue = self.max
        else:
            psmethod.UseLimitMaxValue = False

        if self.min is not None:
            psmethod.UseLimitMinValue = True
            psmethod.LimitMinValue = self.min
        else:
            psmethod.UseLimitMinValue = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        if psmethod.UseLimitMaxValue:
            self.max = single_to_double(psmethod.LimitMaxValue)
        else:
            self.max = None

        if psmethod.UseLimitMinValue:
            self.min = single_to_double(psmethod.LimitMinValue)
        else:
            self.min = None


class ChargeLimits(BaseSettings):
    """Adjust the charge limits.

    Examples
    --------
    As a `ChargeLimits` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import ChargeLimits
    >>> method = ps.ChronoAmperometry(
    ...     charge_limits=ChargeLimits(
    ...         min=5,
    ...         max=200,
    ...     ),
    ... )

    From a dict (coerced to a `ChargeLimits` by Pydantic):

    >>> method = ps.ChronoAmperometry(
    ...     charge_limits={
    ...         'min': 5,
    ...         'max': 200,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.ChronoAmperometry()
    >>> method.charge_limits.min = 5
    >>> method.charge_limits.max = 200
    """

    min: None | float = None
    """Set charge limit min in µC.

    `None` disables the limit."""

    max: None | float = None
    """Set charge limit max in µC.

    `None` disables the limit."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        if self.max is not None:
            psmethod.UseChargeLimitMax = True
            psmethod.ChargeLimitMax = self.max
        else:
            psmethod.UseChargeLimitMax = False

        if self.min is not None:
            psmethod.UseChargeLimitMin = True
            psmethod.ChargeLimitMin = self.min
        else:
            psmethod.UseChargeLimitMin = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        if psmethod.UseChargeLimitMax:
            self.max = single_to_double(psmethod.ChargeLimitMax)
        else:
            self.max = None

        if psmethod.UseChargeLimitMin:
            self.min = single_to_double(psmethod.ChargeLimitMin)
        else:
            self.min = None


class IrDropCompensation(BaseSettings):
    """Set the iR drop compensation settings.

    Examples
    --------
    As a `IrDropCompensation` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import IrDropCompensation
    >>> method = ps.CyclicVoltammetry(
    ...     ir_drop_compensation=IrDropCompensation(
    ...         resistance=50,
    ...     ),
    ... )

    From a dict (coerced to a `IrDropCompensation` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     ir_drop_compensation={
    ...         'resistance': 50,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.ir_drop_compensation.resistance = 50
    """

    resistance: None | float = None
    """Set the iR compensation resistance in Ω"""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        if self.resistance:
            psmethod.UseIRDropComp = True
            psmethod.IRDropCompRes = self.resistance
        else:
            psmethod.UseIRDropComp = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        if psmethod.UseIRDropComp:
            self.resistance = single_to_double(psmethod.IRDropCompRes)
        else:
            self.resistance = None


class EquilibrationTriggers(BaseSettings):
    """Set the equilibration triggers.

    Set one or more digital outputs on the AUX port
    at the start of equilibration.

    The selected digital line(s) will be set to high when triggered
    and remain high until the end of the equilibration.

    See the instrument-specific documentation for more information about
    the position of the digital pins on your instrument’s auxiliary port.

    Examples
    --------
    As a `EquilibrationTriggers` instance, trigger on d0 and d1:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import EquilibrationTriggers
    >>> method = ps.CyclicVoltammetry(
    ...     equilibrion_triggers=EquilibrationTriggers(
    ...         d0=True,
    ...         d1=True,
    ...         d2=False,
    ...         d3=False,
    ...     ),
    ... )

    From a dict (coerced to a `EquilibrationTriggers` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     equilibrion_triggers={
    ...         'd0': True,
    ...         'd1': True,
    ...         'd2': False,
    ...         'd3': False,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.equilibrion_triggers.d0 = True
    >>> method.equilibrion_triggers.d1 = True
    >>> method.equilibrion_triggers.d2 = False
    >>> method.equilibrion_triggers.d3 = False
    """

    d0: bool = False
    """If True, enable trigger at d0 high."""

    d1: bool = False
    """If True, enable trigger at d1 high."""

    d2: bool = False
    """If True, enable trigger at d2 high."""

    d3: bool = False
    """If True, enable trigger at d3 high."""

    def to_list(self) -> list[bool]:
        """Return trigger values as list."""
        return [self.d0, self.d1, self.d2, self.d3]

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        if any(self.to_list()):
            psmethod.UseTriggerOnEquil = True
            psmethod.TriggerValueOnEquil = convert_bools_to_int(self.to_list())
        else:
            psmethod.UseTriggerOnEquil = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        if psmethod.UseTriggerOnEquil:
            self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(
                psmethod.TriggerValueOnEquil
            )
        else:
            self.clear()

    def clear(self):
        """Clear triggers."""
        self.d0 = False
        self.d1 = False
        self.d2 = False
        self.d3 = False


class MeasurementTriggers(BaseSettings):
    """Set the measurement triggers.

    Set one or more digital outputs on the AUX port
    at the start measurement (end of equilibration).

    The selected digital line(s) will be set to high when triggered
    and remain high until the end of the measurement.

    See the instrument-specific documentation for more information about
    the position of the digital pins on your instrument’s auxiliary port.

    Examples
    --------
    As a `MeasurementTriggers` instance, trigger on d0 and d1:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import MeasurementTriggers
    >>> method = ps.CyclicVoltammetry(
    ...     measurement_triggers=MeasurementTriggers(
    ...         d0=True,
    ...         d1=True,
    ...         d2=False,
    ...         d3=False,
    ...     ),
    ... )

    From a dict (coerced to a `MeasurementTriggers` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     measurement_triggers={
    ...         'd0': True,
    ...         'd1': True,
    ...         'd2': False,
    ...         'd3': False,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.measurement_triggers.d0 = True
    >>> method.measurement_triggers.d1 = True
    >>> method.measurement_triggers.d2 = False
    >>> method.measurement_triggers.d3 = False
    """

    d0: bool = False
    """If True, enable trigger at d0 high."""

    d1: bool = False
    """If True, enable trigger at d1 high."""

    d2: bool = False
    """If True, enable trigger at d2 high."""

    d3: bool = False
    """If True, enable trigger at d3 high."""

    def to_list(self) -> list[bool]:
        """Return trigger values as list."""
        return [self.d0, self.d1, self.d2, self.d3]

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        if any(self.to_list()):
            psmethod.UseTriggerOnStart = True
            psmethod.TriggerValueOnStart = convert_bools_to_int(self.to_list())
        else:
            psmethod.UseTriggerOnStart = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        if psmethod.UseTriggerOnStart:
            self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(
                psmethod.TriggerValueOnStart
            )
        else:
            self.clear()

    def clear(self):
        """Clear triggers."""
        self.d0 = False
        self.d1 = False
        self.d2 = False
        self.d3 = False


class DelayTriggers(BaseSettings):
    """Set the delayed measurement triggers.

    Set one or more digital outputs on the AUX port after a delay
    at the start measurement (end of equilibration).

    The selected digital line(s) will be set to high when triggered
    and remain high until the end of the measurement.

    See the instrument-specific documentation for more information about
    the position of the digital pins on your instrument’s auxiliary port.

    Examples
    --------
    As a `DelayTriggers` instance, trigger on d0 and d1:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import DelayTriggers
    >>> method = ps.LinearSweepPotentiometry(
    ...     delay_triggers=DelayTriggers(
    ...         delay=0.5,
    ...         d0=True,
    ...         d1=True,
    ...         d2=False,
    ...         d3=False,
    ...     ),
    ... )

    From a dict (coerced to a `DelayTriggers` by Pydantic):

    >>> method = ps.LinearSweepPotentiometry(
    ...     delay_triggers={
    ...         'delay': 0.5,
    ...         'd0': True,
    ...         'd1': True,
    ...         'd2': False,
    ...         'd3': False,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.LinearSweepPotentiometry()
    >>> method.delay_triggers.delay = 0.5
    >>> method.delay_triggers.d0 = True
    >>> method.delay_triggers.d1 = True
    >>> method.delay_triggers.d2 = False
    >>> method.delay_triggers.d3 = False
    """

    delay: float = 0.5
    """Delay in s after the measurement has started.

    The value will be rounded to interval time * number of data points.
    """

    d0: bool = False
    """If True, enable trigger at d0 high."""

    d1: bool = False
    """If True, enable trigger at d1 high."""

    d2: bool = False
    """If True, enable trigger at d2 high."""

    d3: bool = False
    """If True, enable trigger at d3 high."""

    def to_list(self) -> list[bool]:
        """Return trigger values as list."""
        return [self.d0, self.d1, self.d2, self.d3]

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.TriggerDelayPeriod = self.delay

        if any(self.to_list()):
            psmethod.UseTriggerOnDelay = True
            psmethod.TriggerValueOnDelay = convert_bools_to_int(self.to_list())
        else:
            psmethod.UseTriggerOnDelay = False

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.delay = single_to_double(psmethod.TriggerDelayPeriod)

        if psmethod.UseTriggerOnDelay:
            self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(
                psmethod.TriggerValueOnDelay
            )
        else:
            self.clear()

    def clear(self):
        """Clear triggers."""
        self.d0 = False
        self.d1 = False
        self.d2 = False
        self.d3 = False


class Multiplexer(BaseSettings):
    """Set the multiplexer settings.

    Examples
    --------
    As a `Multiplexer` instance, consecutive on the first 3 channels:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import Multiplexer
    >>> method = ps.LinearSweepPotentiometry(
    ...     multiplexer=Multiplexer(
    ...         mode='consecutive',
    ...         channels=[0,1,2],
    ...         connect_se_we=False,
    ...         combine_re_ce=False,
    ...         common_re_ce=False,
    ...         unused_we='float',
    ...     ),
    ... )

    From a dict (coerced to a `Multiplexer` by Pydantic):

    >>> method = ps.LinearSweepPotentiometry(
    ...     multiplexer={
    ...         'mode': 'consecutive',
    ...         'channels': [0,1,2],
    ...         'connect_se_we': False,
    ...         'combine_re_ce': False,
    ...         'common_re_ce': False,
    ...         'unused_we': 'float',
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.LinearSweepPotentiometry()
    >>> method.multiplexer.mode = 'consecutive'
    >>> method.multiplexer.channels = [0,1,2]
    >>> method.multiplexer.connect_se_we = False
    >>> method.multiplexer.combine_re_ce = False
    >>> method.multiplexer.common_re_ce = False
    >>> method.multiplexer.unused_we = 'float'
    """

    _MODES: tuple[Literal['none', 'consecutive', 'alternate'], ...] = (
        'none',
        'consecutive',
        'alternate',
    )

    _UNUSED_WE_STATES: tuple[Literal['float', 'ground', 'standby'], ...] = (
        'float',
        'ground',
        'standby',
    )

    mode: Literal['none', 'consecutive', 'alternate'] = 'none'
    """Set multiplexer mode.

    - `none`: No multiplexer (disabled).
    - `consecutive`: Channels are measured one at a time, in sequence.
       Any subset of channels may be selected.
    - `alternate`: All selected channels are measured simultaneously by
       rapidly switching between them within each measurement interval.
       Channels must be consecutive starting from 0 (e.g. [0,1,2,3]).
       Only supported by CA, CP, OCP, and (G)EIS.
    """

    channels: list[int] = Field(default_factory=list)
    """Set multiplexer channels.

    This is defined as a list of indexes for which channels to enable (max 128).
    For example, [0,3,7]. In consecutive mode all selections are valid.

    In alternating mode the first channel must be selected and all other
    channels should be consecutive (e.g [0,1,2,3]).
    """

    connect_se_we: bool = False
    """Connect the sense electrode to the working electrode. Default is False."""

    combine_re_ce: bool = False
    """Combine the reference and counter electrodes. Default is False."""

    common_re_ce: bool = False
    """Use channel 1 reference and counter electrodes for all working electrodes. Default is False."""

    unused_we: Literal['float', 'ground', 'standby'] = 'float'
    """State of the unused channel working electrodes:

    - `float`: Disconnected / floating
    - `ground`: Ground
    - `standby`: Standby potential

    Default is `'float'`."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        # Create a mux8r2 multiplexer settings settings object
        mux_mode = self._MODES.index(self.mode) - 1
        psmethod.MuxMethod = PalmSens.MuxMethod(mux_mode)

        # disable all mux channels (range 0-127)
        for i in range(len(psmethod.UseMuxChannel)):
            psmethod.UseMuxChannel[i] = False

        # set the selected mux channels
        for i in self.channels:
            psmethod.UseMuxChannel[i - 1] = True

        psmethod.MuxSett.ConnSEWE = self.connect_se_we
        psmethod.MuxSett.ConnectCERE = self.combine_re_ce
        psmethod.MuxSett.CommonCERE = self.common_re_ce
        unused_we_setting = {
            'float': PalmSens.Method.MuxSettings.UnselWESetting.FLOAT,
            'ground': PalmSens.Method.MuxSettings.UnselWESetting.GND,
            'standby': PalmSens.Method.MuxSettings.UnselWESetting.VSTDBY,
        }[self.unused_we]
        psmethod.MuxSett.UnselWE = unused_we_setting

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.mode = self._MODES[int(psmethod.MuxMethod) + 1]

        self.channels = [
            i + 1 for i in range(len(psmethod.UseMuxChannel)) if psmethod.UseMuxChannel[i]
        ]

        self.connect_se_we = psmethod.MuxSett.ConnSEWE
        self.combine_re_ce = psmethod.MuxSett.ConnectCERE
        self.common_re_ce = psmethod.MuxSett.CommonCERE
        self.unused_we = self._UNUSED_WE_STATES[int(psmethod.MuxSett.UnselWE)]


class DataProcessing(BaseSettings):
    """Set the data processing settings.

    Examples
    --------
    As a `DataProcessing` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import DataProcessing
    >>> method = ps.CyclicVoltammetry(
    ...     data_processing=DataProcessing(
    ...         smooth_level=0,
    ...         min_height=0.0,
    ...         min_width=0.1,
    ...     ),
    ... )

    From a dict (coerced to a `DataProcessing` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     data_processing={
    ...         'smooth_level': 0,
    ...         'min_height': 0.0,
    ...         'min_width': 0.1,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.data_processing.smooth_level = 0
    >>> method.data_processing.min_height = 0.0
    >>> method.data_processing.min_width = 0.1
    """

    smooth_level: int = 0
    """Set the default curve post processing filter.

    Possible values:

    - -1: no filter
    - 0: spike rejection
    - 1: spike rejection + Savitsky-golay window 5
    - 2: spike rejection + Savitsky-golay window 9
    - 3: spike rejection + Savitsky-golay window 15
    - 4: spike rejection + Savitsky-golay window 25
    """

    min_height: float = 0.0
    """Determines the minimum peak height in µA for peak finding.

    Peaks lower than this value are rejected."""

    min_width: float = 0.1
    """The minimum peak width for peak finding.

    The value is in the unit of the curves X axis (V).
    Peaks narrower than this value are rejected (default: 0.1 V)."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.SmoothLevel = self.smooth_level
        psmethod.MinPeakHeight = self.min_height
        psmethod.MinPeakWidth = self.min_width

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.smooth_level = psmethod.SmoothLevel
        self.min_width = single_to_double(psmethod.MinPeakWidth)
        self.min_height = single_to_double(psmethod.MinPeakHeight)


class General(BaseSettings):
    """Sets general/other settings.

    Examples
    --------
    As a `General` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import General
    >>> method = ps.CyclicVoltammetry(
    ...     general=General(
    ...         save_on_internal_storage=False,
    ...         use_hardware_sync=False,
    ...         notes='They asked me if I had a degree in theoretical physics.',
    ...         power_frequency=50,
    ...     ),
    ... )

    From a dict (coerced to a `General` by Pydantic):

    >>> method = ps.CyclicVoltammetry(
    ...     general={
    ...         'save_on_internal_storage': False,
    ...         'use_hardware_sync': False,
    ...         'notes': 'I told them I had a theoretical degree in physics.',
    ...         'power_frequency': 50,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.CyclicVoltammetry()
    >>> method.general.save_on_internal_storage = False
    >>> method.general.use_hardware_sync = False
    >>> method.general.notes = 'They said welcome aboard.'
    >>> method.general.power_frequency = 50
    """

    save_on_internal_storage: bool = False
    """Save on internal storage."""

    use_hardware_sync: bool = False
    """Use hardware synchronization with other channels/instruments."""

    notes: str = ''
    """Add some user notes for use with this technique."""

    power_frequency: Literal[50, 60] = 50
    """Set the DC mains filter in Hz.

    Adjusts sampling on instrument to account for mains frequency.
    Set to 50 Hz or 60 Hz depending on your region (default: 50)."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.SaveOnDevice = self.save_on_internal_storage
        psmethod.UseHWSync = self.use_hardware_sync
        psmethod.Notes = self.notes
        psmethod.PowerFreq = self.power_frequency

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.save_on_internal_storage = psmethod.SaveOnDevice
        self.use_hardware_sync = psmethod.UseHWSync
        self.notes = psmethod.Notes or ''
        self.power_frequency = psmethod.PowerFreq


class Material(BaseSettings):
    """Stores material settings for corrosion measurements.

    Examples
    --------
    As a `Material` instance:

    >>> import pypalmsens as ps
    >>> from pypalmsens.settings import Material
    >>> method = ps.corrosion.CyclicPolarization(
    ...     material=Material(
    ...         surface_area=0.0,
    ...         weight=0.0,
    ...         density=0.0,
    ...         b_anodic=0.0,
    ...         b_cathodic=0.0,
    ...     ),
    ... )

    From a dict (coerced to a `Material` by Pydantic):

    >>> method = ps.corrosion.CyclicPolarization(
    ...     material={
    ...         'surface_area': 0.0,
    ...         'weight': 0.0,
    ...         'density': 0.0,
    ...         'b_anodic': 0.0,
    ...         'b_cathodic': 0.0,
    ...     },
    ... )

    By setting attributes directly:

    >>> method = ps.corrosion.CyclicPolarization()
    >>> method.material.surface_area = 0.0
    >>> method.material.weight = 0.0
    >>> method.material.density = 0.0
    >>> method.material.b_anodic = 0.0
    >>> method.material.b_cathodic = 0.0
    """

    surface_area: float = 0.0
    """Surface area of the sample in cm2."""

    weight: float = 0.0
    """Equivalent mass of one mole of the sample material in g/mol."""

    density: float = 0.0
    """Density of the sample in g/cm3."""

    b_anodic: float = 0.0
    """B anodic in V/dec."""

    b_cathodic: float = 0.0
    """B cathodic in V/dec."""

    @override
    def _export(self, psmethod: PalmSens.Method, /):
        psmethod.Area = self.surface_area
        psmethod.Weight = self.weight
        psmethod.Density = self.density
        psmethod.Ba = self.b_anodic
        psmethod.Bc = self.b_cathodic

    @override
    def _import(self, psmethod: PalmSens.Method, /):
        self.surface_area = psmethod.Area
        self.weight = psmethod.Weight
        self.density = psmethod.Density
        self.b_anodic = psmethod.Ba
        self.b_cathodic = psmethod.Bc


class CustomUnits(BaseModel):
    """Assign a custom unit to the AS / AT / AU variable types in MethodScript."""

    quantity: str | None = None
    """The full name to assign to the variable."""

    symbol: str | None = None
    """Abbreviation of the quantity."""

    unit: str | None = None
    """Abbreviation of the unit of the quantity."""
