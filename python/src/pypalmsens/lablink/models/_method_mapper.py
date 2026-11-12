from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, cast

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
    FastAmperometry,
    LinearSweepPotentiometry,
    LinearSweepVoltammetry,
    MultiplePulseAmperometry,
    MultiStepAmperometry,
    NormalPulseVoltammetry,
    OpenCircuitPotentiometry,
    PulsedAmperometricDetection,
    SquareWaveVoltammetry,
    StrippingChronoPotentiometry,
)
from ..._types import AllowedCurrentRanges, AllowedPotentialRanges
from ._wire import TechniqueId

if TYPE_CHECKING:
    from ..._types import MethodTypeCompatible

ParamDict = dict[str, float | bool | str]

# Technique id -> wire technique name (drives both `Technique` and `Name`).
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
}


class _RawWireValue(str):
    """A number already formatted for the wire, written verbatim instead of quoted.

    C# serializes ranges and plain numbers alike as numbers, so range strings built
    by :func:`_wire_range` must not go through the JSON quoting that applies to
    genuine string parameters such as ``Name``.
    """


class _GroupValue(str):
    """A nested-group count, written verbatim without the ``[...]`` wrapper.

    C# leaves `Stages`, `Levels` and `Curves` values unbracketed (`Levels=2`), while
    the nested `Levels/0/Level/...` values are bracketed as usual.
    """


_SI_EXPONENTS: dict[str, int] = {'p': -12, 'n': -9, 'u': -6, 'm': -3}
"""SI prefixes that appear in the range literals; ``'1A'`` and ``'1V'`` have none."""


def _wire_range(value: AllowedCurrentRanges | AllowedPotentialRanges) -> _RawWireValue:
    """Format a range literal the way C# serializes a `MeasuringRange`.

    C# stores a range as a ``(significant, exponent)`` pair whose exponent is a whole
    SI prefix, and writes it as a ``decimal``, which keeps its scale. Trailing zeros
    therefore matter: ``'100nA'`` is ``0.000000100`` and ``'1mA'`` is ``0.001``, so the
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


def _add_potential_range(p: ParamDict, rng: PotentialRange) -> None:
    p['MinimumPotentialRange'] = _wire_range(rng.min)
    p['MaximumPotentialRange'] = _wire_range(rng.max)
    p['StartingPotentialRange'] = _wire_range(rng.start)


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
    # The C# mapper omits these keys entirely when no resistance is configured.
    if ir.resistance is not None:
        p['UseIRCompensation'] = True
        p['IRCompensation'] = ir.resistance


def _add_post_measurement(p: ParamDict, pm: PostMeasurement) -> None:
    if pm.cell_on_after_measurement:
        p['CellModeAfterMeasurement'] = 'CellModeAfterMeasurementPotentiostatic'
        p['UsePotentialAfterMeasurement'] = True
        p['PotentialAfterMeasurement'] = pm.standby_potential
        p['UseCurrentAfterMeasurement'] = False
        p['UseMeasuredCurrentRangeAfterMeasurement'] = False
        p['UseMeasuredPotentialRangeAfterMeasurement'] = False
    else:
        p['CellModeAfterMeasurement'] = 'CellModeAfterMeasurementOff'


def _add_general(p: ParamDict, gen: General, *, hardware_sync: bool = True) -> None:
    """Only hardware sync maps; mains frequency lives in configure, deferred.

    Pass `hardware_sync=False` for techniques whose C# mapper leaves the key out
    entirely, such as stripping chronopotentiometry.
    """
    # Every C# legacy mapper that writes this hardcodes HardwareSyncIsEnabled = false,
    # so the wire value is always false; forwarding a true here would diverge silently.
    _require_default('use_hardware_sync', gen.use_hardware_sync, False)
    if hardware_sync:
        p['EnableHardwareSync'] = False
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
    # CV has no charge/temperature limit fields; the hub still expects the flags.
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
    # The SWV wire model has no aux/cell/WE-potential keys; the hub records only
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
    # Like SWV, DPV emits no aux/cell/WE-potential keys; guard rather than drop.
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
    # Like SWV/DPV, NPV emits no aux/cell/WE-potential keys; guard rather than drop.
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
    # Fast amperometry fixes one range for minimum, maximum and start; the model field
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
    _add_general(p, m.general, hardware_sync=False)
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
    """Serialize one parameter value, matching C# ``MethodParametersExtensions``."""
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
    """Build the ``StartMeasurementCommand`` body for a technique.

    Values are formatted exactly like the C# mapper writes them, so the result is
    the wire ``dict[str, str]`` the hub expects (``MethodParameters``); ``Technique``
    carries the technique name.

    Notes:

    - Numbers are not JSON-encoded: C# formats doubles with ``G7``, which prints
        ``1`` rather than ``1.0``, and falls back to ``E`` notation for magnitudes
        below ``1e-4`` (for example ``[1E-05]``).

    - Ranges are fixed-point decimals in base units that keep their scale, so
        ``100nA`` is ``[0.000000100]``; see :func:`_wire_range`.

    """
    params = _to_parameters(method)
    return {
        'Technique': ID_TO_TECHNIQUE[method.id].value,
        'MethodParameters': {key: _serialize(value) for key, value in params.items()},
    }
