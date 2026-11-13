from __future__ import annotations

import json
import math
from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from ..._methods.mixed_mode import MixedMode
from ..._methods.settings import (
    CurrentRange,
    General,
    IrDropCompensation,
    PostMeasurement,
    PotentialRange,
    Pretreatment,
    VersusOCP,
)
from ..._methods.techniques import (
    ACVoltammetry,
    ChronoAmperometry,
    ChronoCoulometry,
    ChronoPotentiometry,
    CyclicVoltammetry,
    DifferentialPulseVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    FastAmperometry,
    GalvanostaticImpedanceSpectroscopy,
    LinearSweepPotentiometry,
    LinearSweepVoltammetry,
    MethodScript,
    MultiplePulseAmperometry,
    MultiStepAmperometry,
    MultiStepPotentiometry,
    NormalPulseVoltammetry,
    OpenCircuitPotentiometry,
    PulsedAmperometricDetection,
    SquareWaveVoltammetry,
    StrippingChronoPotentiometry,
)
from ..._types import AllowedCurrentRanges, AllowedPotentialRanges
from ._wire import TechniqueId

if TYPE_CHECKING:
    from ..._methods.mixed_mode import StageType
    from ..._types import MethodTypeCompatible

ParamDict = dict[str, float | bool | str]

ID_TO_TECHNIQUE: dict[str, TechniqueId] = {
    'ad': TechniqueId.Chronoamperometry,
    'cv': TechniqueId.CyclicVoltammetry,
    'lsv': TechniqueId.LinearSweepVoltammetry,
    'swv': TechniqueId.SquareWaveVoltammetry,
    'dpv': TechniqueId.DifferentialPulseVoltammetry,
    'npv': TechniqueId.NormalPulseVoltammetry,
    'pot': TechniqueId.Chronopotentiometry,
    'acv': TechniqueId.ACVoltammetry,
    'fam': TechniqueId.FastAmperometry,
    'ocp': TechniqueId.OpenCircuitPotentiometry,
    'scp': TechniqueId.StrippingChronopotentiometry,
    'lsp': TechniqueId.LinearSweepPotentiometry,
    'pad': TechniqueId.PulsedAmperometricDetection,
    'mpad': TechniqueId.MultiplePulseAmperometry,
    'cc': TechniqueId.Chronocoulometry,
    'ma': TechniqueId.MultiStepAmperometry,
    'mp': TechniqueId.MultiStepPotentiometry,
    'ms': TechniqueId.MethodScriptSandbox,
    'eis': TechniqueId.ElectrochemicalImpedanceSpectroscopy,
    'gis': TechniqueId.GalvanostaticImpedanceSpectroscopy,
    'mm': TechniqueId.MixedMode,
}


class _RawWireValue(str):
    """A number already formatted for the wire, written verbatim instead of quoted.

    C# serializes ranges and plain numbers alike as numbers, so range strings built
    by :func:`_wire_range` must not go through the JSON quoting that applies to
    genuine string parameters such as `Name`.
    """


class _GroupValue(str):
    """A nested-group count, written verbatim without the `[...]` wrapper.

    C# leaves `Stages`, `Levels` and `Curves` values unbracketed (`Levels=2`), while
    the nested `Levels/0/Level/...` values are bracketed as usual.
    """


_SI_EXPONENTS: dict[str, int] = {'p': -12, 'n': -9, 'u': -6, 'm': -3}
"""SI prefixes that appear in the range literals; `'1A'` and `'1V'` have none."""


def _wire_range(value: AllowedCurrentRanges | AllowedPotentialRanges) -> _RawWireValue:
    """Format a range literal the way C# serializes a `MeasuringRange`.

    C# stores a range as a `(significant, exponent)` pair whose exponent is a whole
    SI prefix, and writes it as a `decimal`, which keeps its scale. Trailing zeros
    therefore matter: `'100nA'` is `0.000000100` and `'1mA'` is `0.001`, so the
    string is built from the prefix instead of from a float division.
    """
    body = value[:-1]  # drop the unit character ('A' or 'V')
    prefix = body[-1] if body[-1] in _SI_EXPONENTS else ''
    significant = int(body[: len(body) - len(prefix)])
    exponent = _SI_EXPONENTS.get(prefix, 0)

    if exponent >= 0:
        return _RawWireValue(str(significant * 10**exponent))
    scale = -exponent
    whole, fraction = divmod(significant, 10**scale)
    return _RawWireValue(f'{whole}.{fraction:0{scale}d}')


def _add_current_range(p: ParamDict, rng: CurrentRange) -> None:
    p['MinimumCurrentRange'] = _wire_range(rng.min)
    p['MaximumCurrentRange'] = _wire_range(rng.max)
    p['StartingCurrentRange'] = _wire_range(rng.start)


_SUPPORTED_POTENTIAL_RANGES: tuple[AllowedPotentialRanges, ...] = ('1mV', '10mV', '100mV', '1V')
"""The potential ranges the legacy `RangingPotential` supports. `AllowedPotentialRanges` offers more.

Measured against the built DLL: any other literal snaps **up** to the next supported range, and
the start range is additionally clamped into the snapped min/max window.
"""


def _snap_potential_range(value: AllowedPotentialRanges) -> AllowedPotentialRanges:
    """Snap a potential range up to the smallest one the legacy ranging supports."""
    volts = float(_wire_range(value))
    for supported in _SUPPORTED_POTENTIAL_RANGES:
        if volts <= float(_wire_range(supported)):
            return supported
    return _SUPPORTED_POTENTIAL_RANGES[-1]


def _add_potential_range(p: ParamDict, rng: PotentialRange) -> None:
    minimum = _snap_potential_range(rng.min)
    maximum = _snap_potential_range(rng.max)
    start = _snap_potential_range(rng.start)
    # The legacy getter clamps the start range into the window, and the minimum wins when the
    # window is inverted (min > max).
    clamped = max(
        float(_wire_range(minimum)), min(float(_wire_range(start)), float(_wire_range(maximum)))
    )
    p['MinimumPotentialRange'] = _wire_range(minimum)
    p['MaximumPotentialRange'] = _wire_range(maximum)
    p['StartingPotentialRange'] = next(
        _wire_range(supported)
        for supported in _SUPPORTED_POTENTIAL_RANGES
        if float(_wire_range(supported)) == clamped
    )


def _add_pretreatment(p: ParamDict, pre: Pretreatment) -> None:
    p['ConditioningPotential'] = pre.conditioning_potential
    p['ConditioningTime'] = pre.conditioning_time
    p['DepositionPotential'] = pre.deposition_potential
    p['DepositionTime'] = pre.deposition_time


def _add_vs_ocp(p: ParamDict, versus_ocp: VersusOCP) -> None:
    """Emit the OCP determination group that C# `AddVsOcpParameters` writes.

    The group is gated on the legacy `IsVersusOCP` flag, which pypalmsens sets
    whenever `potentials` is non-empty (see `VersusOCP._export`).
    """
    if not versus_ocp.potentials:
        return
    p['EnableOcp'] = True
    p['MaximumOCPTime'] = versus_ocp.timeout
    p['OCPStabilityCriterion'] = versus_ocp.stability_criterion


def _add_limits(
    p: ParamDict,
    kind: str,
    minimum: float | None,
    maximum: float | None,
    *,
    prefix: str = '',
) -> None:
    """Emit a Use/value limit pair, optionally nested under a group key prefix."""
    p[f'{prefix}UseMinimum{kind}Limit'] = minimum is not None
    p[f'{prefix}UseMaximum{kind}Limit'] = maximum is not None
    if minimum is not None:
        p[f'{prefix}Minimum{kind}Limit'] = minimum
    if maximum is not None:
        p[f'{prefix}Maximum{kind}Limit'] = maximum


def _add_ir_drop_compensation(p: ParamDict, ir: IrDropCompensation) -> None:
    """Omit these keys entirely when no resistance is configured."""
    if ir.resistance is not None:
        p['UseIRCompensation'] = True
        p['IRCompensation'] = ir.resistance


def _add_post_measurement(p: ParamDict, pm: PostMeasurement) -> None:
    """The legacy methods only support potentiostatic mode after measurement.

    TODO: In the future we need to add support for Galvanostatic / other cell modes.
    """
    if pm.cell_on_after_measurement:
        p['CellModeAfterMeasurement'] = 'CellModeAfterMeasurementPotentiostatic'
        p['UsePotentialAfterMeasurement'] = True
        p['PotentialAfterMeasurement'] = pm.standby_potential
        p['UseCurrentAfterMeasurement'] = False
        p['UseMeasuredCurrentRangeAfterMeasurement'] = False
        p['UseMeasuredPotentialRangeAfterMeasurement'] = False
    else:
        p['CellModeAfterMeasurement'] = 'CellModeAfterMeasurementOff'


def _add_general(p: ParamDict, gen: General) -> None:
    """Only hardware sync maps; mains frequency lives in configure, deferred.

    Pass `hardware_sync=False` for techniques whose C# mapper leaves the key out
    entirely, such as stripping chronopotentiometry.
    """
    default = General()

    # Every C# legacy mapper that writes this hardcodes HardwareSyncIsEnabled = false,
    # so the wire value is always false; forwarding a true here would diverge silently.
    if gen.use_hardware_sync:
        raise ValueError(
            'Lablink does not support setting hardware sync on the method. '
            'Use `Instrument.configure` to enable hardware sync.'
        )
    if gen.power_frequency != default.power_frequency:
        raise ValueError(
            'Lablink does not support setting the mains frequency on the method. '
            'Use `Instrument.configure` to set mains frequency.'
        )
    if gen.save_on_internal_storage:
        raise NotImplementedError("Lablink does not yet support 'save_on_internal_storage'")
    if gen.notes:
        raise NotImplementedError("Lablink does not yet support 'notes'")


def _require_default(name: str, value: object, default: object) -> None:
    """Raise if a still-unsupported setting differs from its default."""
    if value != default:
        raise NotImplementedError(f'Lablink does not yet support {name!r}')


def _build_chronoamperometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(ChronoAmperometry, method)
    default = ChronoAmperometry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['IntervalTime'] = m.interval_time
    p['Potential'] = m.potential
    p['RunTime'] = m.run_time

    # Chronoamperometry only supports 'potential' versus OCP.
    p['PotentialOCP'] = 'potential' in m.versus_ocp.potentials
    _add_vs_ocp(p, m.versus_ocp)

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    _add_limits(p, 'Charge', m.charge_limits.min, m.charge_limits.max)
    _add_limits(p, 'Temperature', None, None)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureCellPotential'] = m.record_cell_potential
    p['MeasureWEPotential'] = m.record_we_potential

    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _build_chronopotentiometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(ChronoPotentiometry, method)
    default = ChronoPotentiometry()

    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_potential_range(p, m.potential_range)
    _add_pretreatment(p, m.pretreatment)

    p['AppliedCurrent'] = m.current
    p['AppliedCurrentRange'] = _wire_range(m.applied_current_range)
    p['IntervalTime'] = m.interval_time
    p['RunTime'] = m.run_time

    _add_limits(p, 'Potential', m.potential_limits.min, m.potential_limits.max)
    # Chronopotentiometry has no charge limits, but C# still writes the temperature
    # limit flags.
    _add_limits(p, 'Temperature', None, None)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureWECurrent'] = m.record_we_current

    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _build_cyclicvoltammetry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(CyclicVoltammetry, method)
    default = CyclicVoltammetry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['BeginPotential'] = m.begin_potential
    p['Vertex1Potential'] = m.vertex1_potential
    p['Vertex2Potential'] = m.vertex2_potential
    p['StepPotential'] = m.step_potential
    p['ScanRate'] = m.scanrate
    p['NumberOfScans'] = m.n_scans

    # CV OCP is per-potential, not a shared EnableOCP flag.
    p['BeginPotentialOCP'] = 'begin' in m.versus_ocp.potentials
    p['Vertex1PotentialOCP'] = 'vertex1' in m.versus_ocp.potentials
    p['Vertex2PotentialOCP'] = 'vertex2' in m.versus_ocp.potentials
    _add_vs_ocp(p, m.versus_ocp)

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    # CV has no charge/temperature limit fields. Lablink still expects the flags.
    _add_limits(p, 'Charge', None, None)
    _add_limits(p, 'Temperature', None, None)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureCellPotential'] = m.record_cell_potential
    p['MeasureWEPotential'] = m.record_we_potential

    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _build_linearsweepvoltammetry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(LinearSweepVoltammetry, method)
    default = LinearSweepVoltammetry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['BeginPotential'] = m.begin_potential
    p['EndPotential'] = m.end_potential
    p['StepPotential'] = m.step_potential
    p['ScanRate'] = m.scanrate

    # LSV OCP is per-potential (begin/end), not a shared EnableOCP flag.
    p['BeginPotentialOCP'] = 'begin' in m.versus_ocp.potentials
    p['EndPotentialOCP'] = 'end' in m.versus_ocp.potentials
    _add_vs_ocp(p, m.versus_ocp)

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    _add_limits(p, 'Charge', None, None)
    _add_limits(p, 'Temperature', None, None)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureCellPotential'] = m.record_cell_potential
    p['MeasureWEPotential'] = m.record_we_potential

    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _build_squarewavevoltammetry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(SquareWaveVoltammetry, method)
    default = SquareWaveVoltammetry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )
    # The SWV wire model has no aux/cell/WE-potential keys. Lablink records only
    # forward/reverse currents here. Raise rather than silently drop these.
    _require_default(
        'record_auxiliary_input',
        m.record_auxiliary_input,
        default.record_auxiliary_input,
    )
    _require_default(
        'record_cell_potential', m.record_cell_potential, default.record_cell_potential
    )
    _require_default('record_we_potential', m.record_we_potential, default.record_we_potential)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['BeginPotential'] = m.begin_potential
    p['EndPotential'] = m.end_potential
    p['StepPotential'] = m.step_potential
    p['Frequency'] = m.frequency
    p['Amplitude'] = m.amplitude

    p['BeginPotentialOCP'] = 'begin' in m.versus_ocp.potentials
    p['EndPotentialOCP'] = 'end' in m.versus_ocp.potentials
    _add_vs_ocp(p, m.versus_ocp)

    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureCurrentForwardReverse'] = m.record_forward_and_reverse_currents
    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _build_differentialpulsevoltammetry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(DifferentialPulseVoltammetry, method)
    default = DifferentialPulseVoltammetry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )
    # Like SWV, DPV emits no aux/cell/WE-potential keys. Guard rather than drop.
    _require_default(
        'record_auxiliary_input',
        m.record_auxiliary_input,
        default.record_auxiliary_input,
    )
    _require_default(
        'record_cell_potential', m.record_cell_potential, default.record_cell_potential
    )
    _require_default('record_we_potential', m.record_we_potential, default.record_we_potential)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['BeginPotential'] = m.begin_potential
    p['EndPotential'] = m.end_potential
    p['StepPotential'] = m.step_potential
    p['PulsePotential'] = m.pulse_potential
    p['PulseTime'] = m.pulse_time
    p['ScanRate'] = m.scan_rate

    p['BeginPotentialOCP'] = 'begin' in m.versus_ocp.potentials
    p['EndPotentialOCP'] = 'end' in m.versus_ocp.potentials
    _add_vs_ocp(p, m.versus_ocp)

    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _build_normalpulsevoltammetry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(NormalPulseVoltammetry, method)
    default = NormalPulseVoltammetry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )
    # Like SWV/DPV, NPV emits no aux/cell/WE-potential keys. Guard rather than drop.
    _require_default(
        'record_auxiliary_input',
        m.record_auxiliary_input,
        default.record_auxiliary_input,
    )
    _require_default(
        'record_cell_potential', m.record_cell_potential, default.record_cell_potential
    )
    _require_default('record_we_potential', m.record_we_potential, default.record_we_potential)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['BeginPotential'] = m.begin_potential
    p['EndPotential'] = m.end_potential
    p['StepPotential'] = m.step_potential
    p['PulseTime'] = m.pulse_time
    p['ScanRate'] = m.scan_rate

    p['BeginPotentialOCP'] = 'begin' in m.versus_ocp.potentials
    p['EndPotentialOCP'] = 'end' in m.versus_ocp.potentials
    _add_vs_ocp(p, m.versus_ocp)

    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False

    _add_general(p, m.general)
    return p


def _add_levels(p: ParamDict, levels: list, *, amperometric: bool) -> None:
    """Emit the multistep `Levels` count plus one `Levels/<i>/Level/...` group each."""
    p['Levels'] = _GroupValue(str(len(levels)))
    for index, level in enumerate(levels):
        base = f'Levels/{index}/Level/'
        if amperometric:
            p[base + 'Potential'] = level.level
            p[base + 'RunTime'] = level.duration
            _add_limits(
                p, 'Current', level.limit_current_min, level.limit_current_max, prefix=base
            )
        else:
            p[base + 'AppliedCurrent'] = level.level
            p[base + 'RunTime'] = level.duration
            _add_limits(
                p,
                'Potential',
                level.limit_potential_min,
                level.limit_potential_max,
                prefix=base,
            )
        p[base + 'RecordLevel'] = level.record


def _build_acvoltammetry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(ACVoltammetry, method)
    default = ACVoltammetry()

    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['BeginPotential'] = m.begin_potential
    p['BeginPotentialOCP'] = 'begin' in m.versus_ocp.potentials
    p['EndPotential'] = m.end_potential
    p['EndPotentialOCP'] = 'end' in m.versus_ocp.potentials
    p['StepPotential'] = m.step_potential
    p['SineWaveAmplitude'] = m.ac_potential
    p['Frequency'] = m.frequency
    p['ScanRate'] = m.scanrate
    p['MeasureDCCurrent'] = m.measure_dc_current

    # ACV emits no limit keys and no aux/cell/WE-potential keys.
    _require_default('versus_ocp potentials used', len(m.versus_ocp.potentials), 0)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_fastamperometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(FastAmperometry, method)
    default = FastAmperometry()

    # The C# fast amperometry mapper writes no limit, iR or BiPot keys at all.
    _require_default('current_limits', m.current_limits, default.current_limits)
    _require_default('charge_limits', m.charge_limits, default.charge_limits)
    _require_default(
        'ir_drop_compensation', m.ir_drop_compensation, default.ir_drop_compensation
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    # Fast amperometry fixes one range for minimum, maximum and start. The model field
    # is a bare range literal, so it goes through `_wire_range` three times.
    fixed_range = _wire_range(m.current_range)
    p['MinimumCurrentRange'] = fixed_range
    p['MaximumCurrentRange'] = fixed_range
    p['StartingCurrentRange'] = fixed_range
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['EquilibrationPotential'] = m.equilibration_potential
    # The legacy OCPmode bit for the equilibration potential has no OCPFlag value.
    p['EquilibrationPotentialOCP'] = False
    p['Potential'] = m.potential
    p['PotentialOCP'] = 'potential' in m.versus_ocp.potentials
    p['IntervalTime'] = m.interval_time
    p['RunTime'] = m.run_time

    _add_vs_ocp(p, m.versus_ocp)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_opencircuitpotentiometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(OpenCircuitPotentiometry, method)
    default = OpenCircuitPotentiometry()

    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_potential_range(p, m.potential_range)
    _add_pretreatment(p, m.pretreatment)

    p['IntervalTime'] = m.interval_time
    p['RunTime'] = m.run_time

    _add_limits(p, 'Potential', m.potential_limits.min, m.potential_limits.max)
    _add_limits(p, 'Temperature', None, None)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureWECurrent'] = m.record_we_current
    # OCP measures with its own current range.
    p['MeasuredCurrentRange'] = _wire_range(m.record_we_current_range)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_strippingchronopotentiometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(StrippingChronoPotentiometry, method)
    default = StrippingChronoPotentiometry()

    # Stripping maps neither the potential range nor hardware sync, and no bandwidth.
    _require_default('potential_range', m.potential_range, default.potential_range)
    _require_default('bandwidth', m.bandwidth, default.bandwidth)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EndPotential'] = m.end_potential
    p['AppliedCurrent'] = m.current
    p['AppliedCurrentRange'] = _wire_range(m.applied_current_range)
    p['MeasurementTime'] = m.measurement_time

    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_linearsweeppotentiometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(LinearSweepPotentiometry, method)
    default = LinearSweepPotentiometry()

    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default('delay_triggers', m.delay_triggers, default.delay_triggers)
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_potential_range(p, m.potential_range)
    _add_pretreatment(p, m.pretreatment)

    p['AppliedCurrentRange'] = _wire_range(m.applied_current_range)
    p['BeginCurrent'] = m.current_begin
    p['EndCurrent'] = m.current_end
    p['StepCurrent'] = m.current_step
    p['ScanRate'] = m.scan_rate

    _add_limits(p, 'Potential', m.potential_limits.min, m.potential_limits.max)
    _add_limits(p, 'Temperature', None, None)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureWECurrent'] = m.record_we_current

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


_PAD_MODES: dict[str, str] = {
    'dc': 'PADModeEdc',
    'pulse': 'PADModePulse',
    'differential': 'PADModeDifferential',
}


def _build_pulsedamperometricdetection(method: MethodTypeCompatible) -> ParamDict:
    m = cast(PulsedAmperometricDetection, method)
    default = PulsedAmperometricDetection()

    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)
    _require_default('delay_triggers', m.delay_triggers, default.delay_triggers)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['PotentialDirectCurrent'] = m.potential
    p['PulsePotential'] = m.pulse_potential
    p['PulseTime'] = m.pulse_time
    p['PADMode'] = _PAD_MODES[m.mode]
    p['RunTime'] = m.run_time
    p['IntervalTime'] = m.interval_time

    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_multiplepulseamperometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(MultiplePulseAmperometry, method)

    _require_default(
        'data_processing', m.data_processing, MultiplePulseAmperometry().data_processing
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['Potential1'] = m.potential_1
    p['Time1'] = m.duration_1
    p['Potential2'] = m.potential_2
    p['Time2'] = m.duration_2
    p['Potential3'] = m.potential_3
    p['Time3'] = m.duration_3
    p['RunTime'] = m.run_time

    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_chronocoulometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(ChronoCoulometry, method)
    default = ChronoCoulometry()

    _require_default('bandwidth', m.bandwidth, default.bandwidth)
    _require_default('data_processing', m.data_processing, default.data_processing)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['IntervalTime'] = m.interval_time
    # Unlike Levels, the coulometry steps are written without a `Steps` count key.
    for index, (potential, run_time) in enumerate(
        ((m.step1_potential, m.step1_run_time), (m.step2_potential, m.step2_run_time))
    ):
        base = f'Steps/{index}/Step/'
        p[base + 'Potential'] = potential
        p[base + 'RunTime'] = run_time

    _add_limits(p, 'Charge', m.charge_limits.min, m.charge_limits.max)
    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureCellPotential'] = m.record_cell_potential
    p['MeasureWEPotential'] = m.record_we_potential

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_multistepamperometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(MultiStepAmperometry, method)
    default = MultiStepAmperometry()

    _require_default(
        'enable_bipot_current', m.enable_bipot_current, default.enable_bipot_current
    )
    _require_default('bipot', m.bipot, default.bipot)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['IntervalTime'] = m.interval_time
    p['NumberOfCycles'] = m.n_cycles
    _add_levels(p, m.levels, amperometric=True)

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    p['SelectLimitPerLevel'] = any(level.use_limits for level in m.levels)
    p['SelectRecordPerLevel'] = any(level.record for level in m.levels)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureCellPotential'] = m.record_cell_potential
    p['MeasureWEPotential'] = m.record_we_potential

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_multistepotentiometry(method: MethodTypeCompatible) -> ParamDict:
    m = cast(MultiStepPotentiometry, method)
    default = MultiStepPotentiometry()

    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('data_processing', m.data_processing, default.data_processing)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_potential_range(p, m.potential_range)
    _add_pretreatment(p, m.pretreatment)

    p['AppliedCurrentRange'] = _wire_range(m.applied_current_range)
    p['IntervalTime'] = m.interval_time
    p['NumberOfCycles'] = m.n_cycles
    _add_levels(p, m.levels, amperometric=False)

    _add_limits(p, 'Potential', m.potential_limits.min, m.potential_limits.max)
    # Same aggregation as `MultiStepPotentiometry._export`, which sets the legacy flags.
    p['SelectLimitPerLevel'] = any(level.use_limits for level in m.levels)
    p['SelectRecordPerLevel'] = any(level.record for level in m.levels)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = m.record_auxiliary_input
    p['MeasureWECurrent'] = m.record_we_current

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_methodscript(method: MethodTypeCompatible) -> ParamDict:
    m = cast(MethodScript, method)
    return {'Script': f'e\n{m.script}\n'}


def _frequencies_per_decade(
    n_frequencies: int, max_frequency: float, min_frequency: float
) -> float:
    """Recompute `NumberOfFrequenciesPerDecade`, which the EIS/GIS records derive.

    The domain records expose it as a computed property rather than a stored field, so the
    mapper always writes it even though no legacy field carries it:
    `(n - 1) / (log10(max) - log10(min))`. A zero denominator means an empty frequency range;
    C# would write `NaN` or `∞` there, which the hub cannot parse, so it is rejected instead.
    """
    if max_frequency == min_frequency:
        raise ValueError('Min frequency cannot be equal to max frequency.')

    denominator = math.log10(max_frequency) - math.log10(min_frequency)
    return float(format((n_frequencies - 1) / denominator, '.7g'))


def _build_eis(method: MethodTypeCompatible) -> ParamDict:
    """Map a potentiostatic impedance frequency scan.

    `max_equilibration_time` lands in the legacy `MaxEqTime` field, which no domain mapper
    reads. The DLL accepts the setting and drops it, so the port drops it too.
    """
    m = cast(ElectrochemicalImpedanceSpectroscopy, method)
    default = ElectrochemicalImpedanceSpectroscopy()

    # The domain model represents exactly one EIS shape: a frequency scan at a fixed dc
    # potential. The legacy mapper returns null for every other scan/frequency combination,
    # which then throws in `TechniqueParametersMappers.ToEntity` (PLAN.md §6), so there is no
    # reference output to match for those.
    _require_default('scan_type', m.scan_type, default.scan_type)
    _require_default('frequency_type', m.frequency_type, default.frequency_type)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default('material', m.material, default.material)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_potential_range(p, m.potential_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    # `BeginPotential` is an alias of `Potential`, which `_export` sets from `dc_potential`.
    p['PotentialDirectCurrent'] = m.dc_potential
    # With a fixed scan type the only OCP flag EIS offers is 'potential', i.e. OCPmode bit 0.
    p['PotentialDirectCurrentOCP'] = 'potential' in m.versus_ocp.potentials
    p['PotentialAlternatingCurrent'] = m.ac_potential
    p['NumberOfFrequencies'] = m.n_frequencies
    p['NumberOfFrequenciesPerDecade'] = _frequencies_per_decade(
        m.n_frequencies, m.max_frequency, m.min_frequency
    )
    p['MaximumFrequency'] = m.max_frequency
    p['MinimumFrequency'] = m.min_frequency
    # `ShowTDDMS` has no pypalmsens setting, so the legacy default is what C# stores.
    p['RecordTimeDomainData'] = False
    p['MinimumSamplingTime'] = m.min_sampling_time

    # The EIS mapper hardcodes null limits, so only the `Use...` flags reach the wire.
    _add_limits(p, 'Current', None, None)
    _add_limits(p, 'Charge', None, None)
    _add_limits(p, 'Temperature', None, None)
    _add_vs_ocp(p, m.versus_ocp)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _build_gis(method: MethodTypeCompatible) -> ParamDict:
    """Map a galvanostatic impedance scan.

    `max_equilibration_time` lands in the legacy `MaxEqTime` field, which no domain mapper
    reads; the DLL accepts the setting and drops it, so the port drops it too.
    """
    m = cast(GalvanostaticImpedanceSpectroscopy, method)
    default = GalvanostaticImpedanceSpectroscopy()

    # Same restriction as EIS, with dc current instead of dc potential.
    _require_default('scan_type', m.scan_type, default.scan_type)
    _require_default('frequency_type', m.frequency_type, default.frequency_type)
    _require_default('multiplexer', m.multiplexer, default.multiplexer)
    _require_default(
        'equilibration_triggers', m.equilibration_triggers, default.equilibration_triggers
    )
    _require_default(
        'measurement_triggers', m.measurement_triggers, default.measurement_triggers
    )

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    _add_potential_range(p, m.potential_range)
    _add_pretreatment(p, m.pretreatment)

    p['EquilibrationTime'] = m.equilibration_time
    p['AppliedCurrentRange'] = _wire_range(m.applied_current_range)
    # Currents are factors of `applied_current_range`, stored as `CurrentIcr` (plain G7).
    p['DCCurrent'] = m.dc_current
    p['ACCurrent'] = m.ac_current
    p['NumberOfFrequencies'] = m.n_frequencies
    p['NumberOfFrequenciesPerDecade'] = _frequencies_per_decade(
        m.n_frequencies, m.max_frequency, m.min_frequency
    )
    p['MaximumFrequency'] = m.max_frequency
    p['MinimumFrequency'] = m.min_frequency
    p['RecordTimeDomainData'] = False
    p['MinimumSamplingTime'] = m.min_sampling_time

    # GIS has no versus-OCP group: its record does not implement `IVsOcpParameters`, and the
    # limits are hardcoded null just like EIS.
    _add_limits(p, 'Potential', None, None)
    _add_limits(p, 'Charge', None, None)
    _add_limits(p, 'Temperature', None, None)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    _add_general(p, m.general)
    return p


def _add_stage(p: ParamDict, index: int, stage: StageType) -> None:
    """Emit one stage, nested under `Stages/<index>/<group>/`.

    The `…VersusPrevious` flags come from the legacy `VsEiPropertiesList`, which pypalmsens
    never populates: no stage setting feeds it, so the DLL stores its default of `false` for
    every stage (measured). Emitting them is still required because
    `MixedModeStageMapper.AddParameters` writes them unconditionally.
    """
    if stage.stage_type == 'ConstantE':
        prefix = f'Stages/{index}/ConstantPotentialStage/'
        p[f'{prefix}Potential'] = stage.potential
        p[f'{prefix}PotentialVersusPrevious'] = False
        p[f'{prefix}RunTime'] = stage.run_time
        _add_limits(
            p, 'Current', stage.current_limits.min, stage.current_limits.max, prefix=prefix
        )
    elif stage.stage_type == 'ConstantI':
        prefix = f'Stages/{index}/ConstantCurrentStage/'
        p[f'{prefix}AppliedCurrentRange'] = _wire_range(stage.applied_current_range)
        # `current` is a factor of `applied_current_range`, stored as a plain double.
        p[f'{prefix}AppliedCurrent'] = stage.current
        p[f'{prefix}AppliedCurrentVersusPrevious'] = False
        p[f'{prefix}RunTime'] = stage.run_time
        _add_limits(
            p,
            'Potential',
            stage.potential_limits.min,
            stage.potential_limits.max,
            prefix=prefix,
        )
    elif stage.stage_type == 'SweepE':
        prefix = f'Stages/{index}/SweepPotentialStage/'
        p[f'{prefix}BeginPotential'] = stage.begin_potential
        p[f'{prefix}BeginPotentialVersusPrevious'] = False
        p[f'{prefix}EndPotential'] = stage.end_potential
        p[f'{prefix}EndPotentialVersusPrevious'] = False
        p[f'{prefix}StepPotential'] = stage.step_potential
        p[f'{prefix}ScanRate'] = stage.scanrate
        _add_limits(
            p, 'Current', stage.current_limits.min, stage.current_limits.max, prefix=prefix
        )
    elif stage.stage_type == 'OpenCircuit':
        prefix = f'Stages/{index}/OpenCircuitStage/'
        p[f'{prefix}RunTime'] = stage.run_time
        _add_limits(
            p,
            'Potential',
            stage.potential_limits.min,
            stage.potential_limits.max,
            prefix=prefix,
        )
    else:
        # TODO: Support Impedance, this is not yet supported on the Lablink side
        raise NotImplementedError(f'Lablink does not support the {stage.stage_type!r} stage')


def _build_mixed_mode(method: MethodTypeCompatible) -> ParamDict:
    """Map mixed mode, whose stages nest under `Stages/<index>/<group>/`.

    Per-stage measurement triggers reach only the parent's `UseTriggerOnStart` legacy field,
    which no domain mapper reads, so they are dropped exactly as the DLL drops them.
    """
    m = cast(MixedMode, method)
    default = MixedMode()

    _require_default('data_processing', m.data_processing, default.data_processing)

    p: ParamDict = {}
    _add_current_range(p, m.current_range)
    # MixedMode offers no `potential_range` setting, so the legacy `RangingPotential` keeps
    # its own defaults; C# reads them anyway because the technique record requires the triple.
    p['MinimumPotentialRange'] = _wire_range('1mV')
    p['MaximumPotentialRange'] = _wire_range('1V')
    p['StartingPotentialRange'] = _wire_range('1V')
    _add_pretreatment(p, m.pretreatment)

    p['IntervalTime'] = m.interval_time
    p['NumberOfCycles'] = m.cycles
    # `Stages` is a bare count, like `Levels`; the per-stage keys below are bracketed as usual.
    p['Stages'] = _GroupValue(str(len(m.stages)))
    for index, stage in enumerate(m.stages):
        _add_stage(p, index, stage)

    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = False
    # The legacy mapper hardcodes `HardwareSyncIsEnabled = false`, like every other technique.
    _add_general(p, m.general)
    return p


_BUILDERS: dict[str, Callable[[MethodTypeCompatible], ParamDict]] = {
    'ad': _build_chronoamperometry,
    'cv': _build_cyclicvoltammetry,
    'lsv': _build_linearsweepvoltammetry,
    'swv': _build_squarewavevoltammetry,
    'dpv': _build_differentialpulsevoltammetry,
    'npv': _build_normalpulsevoltammetry,
    'pot': _build_chronopotentiometry,
    'acv': _build_acvoltammetry,
    'fam': _build_fastamperometry,
    'ocp': _build_opencircuitpotentiometry,
    'scp': _build_strippingchronopotentiometry,
    'lsp': _build_linearsweeppotentiometry,
    'pad': _build_pulsedamperometricdetection,
    'mpad': _build_multiplepulseamperometry,
    'cc': _build_chronocoulometry,
    'ma': _build_multistepamperometry,
    'mp': _build_multistepotentiometry,
    'ms': _build_methodscript,
    'eis': _build_eis,
    'gis': _build_gis,
    'mm': _build_mixed_mode,
}


def _to_parameters(method: MethodTypeCompatible) -> ParamDict:
    """Build the decoded parameter dict for a technique."""
    builder = _BUILDERS.get(method.id)
    if builder is None:
        raise NotImplementedError(f'Lablink does not support technique id {method.id!r}')

    params = builder(method)
    params['Name'] = ID_TO_TECHNIQUE[method.id].value
    return params


def _serialize(value: float | bool | str) -> str:
    """Serialize one parameter value, matching C# `MethodParametersExtensions`."""
    if isinstance(value, _GroupValue):
        # Group counts are written bare, without the [...] wrapper.
        return str(value)
    if isinstance(value, _RawWireValue):
        ret = str(value)
    elif isinstance(value, bool):
        ret = 'true' if value else 'false'
    elif isinstance(value, str):
        ret = json.dumps(value)
    elif isinstance(value, int):
        ret = str(value)
    else:
        mantissa, _, exponent = format(float(value), '.7g').partition('e')
        if exponent:
            ret = f'{mantissa}E{int(exponent):+03d}'
        else:
            ret = mantissa

    return f'[{ret}]'


def to_payload(method: MethodTypeCompatible) -> dict[str, object]:
    """Build the `StartMeasurementCommand` payload for a technique.

    Values are formatted exactly like the C# mapper writes them.
    This matches the `dict[str, str]` the hub expects (`MethodParameters`).

    Notes:

    - Numbers are not JSON-encoded: C# formats doubles with `G7`, which prints
        `1` rather than `1.0`, and falls back to `E` notation for magnitudes
        below `1e-4` (for example `[1E-05]`).

    - Ranges are fixed-point decimals in base units that keep their scale, so
        `100nA` is `[0.000000100]`. See [_wire_range][]

    """
    params = _to_parameters(method)
    return {
        'Technique': ID_TO_TECHNIQUE[method.id].value,
        'MethodParameters': {key: _serialize(value) for key, value in params.items()},
    }
