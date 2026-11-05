"""Convert new-style technique settings into Lablink measurement parameters.

This module avoids the Lablink SDK mapper DLL: it reads technique settings and
builds the wire ``MethodParameters`` without going through ``MethodMappers``.
It uses the core ``PalmSens`` converters (e.g. ``cr_string_to_enum``), which the
rest of the SDK needs anyway.

Design shape:

- ``ID_TO_TECHNIQUE`` maps the technique ``id`` to the wire ``TechniqueId``.
- Shared ``_add_*`` helpers emit the settings groups that are common across
  techniques (ranges, pretreatment, limits, iR, post-measurement, general).
- Each ``_build_*`` function casts the ``MethodTypeCompatible`` protocol to the
  concrete pydantic technique, raises on still-unsupported settings, and emits
  the technique-specific keys by composing the shared helpers.
- ``to_payload`` JSON-encodes the values into the ``StartMeasurementCommand``
  body sent to the hub.

Reading typed attributes (rather than ``to_dict()``) keeps field access
compile-checked: a renamed or missing field fails type-checking instead of
silently dropping a wire key. The dependency stays ``lablink -> _methods``;
``_methods`` never imports ``lablink``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from ..._converters import cr_string_to_enum, pr_string_to_enum
from ..._methods.settings import (
    CurrentRange,
    General,
    IrDropCompensation,
    PostMeasurement,
    PotentialRange,
    Pretreatment,
)
from ..._methods.techniques import (
    ChronoAmperometry,
    ChronoPotentiometry,
    CyclicVoltammetry,
    DifferentialPulseVoltammetry,
    LinearSweepVoltammetry,
    NormalPulseVoltammetry,
    SquareWaveVoltammetry,
)
from ..._types import AllowedCurrentRanges, AllowedPotentialRanges
from ._wire import TechniqueId

if TYPE_CHECKING:
    from ..._types import MethodTypeCompatible

ParamDict = dict[str, list[float | bool | str]]

# Technique id -> wire technique name (drives both `Technique` and `Name`).
ID_TO_TECHNIQUE: dict[str, TechniqueId] = {
    'ad': TechniqueId.Chronoamperometry,
    'cv': TechniqueId.CyclicVoltammetry,
    'lsv': TechniqueId.LinearSweepVoltammetry,
    'swv': TechniqueId.SquareWaveVoltammetry,
    'dpv': TechniqueId.DifferentialPulseVoltammetry,
    'npv': TechniqueId.NormalPulseVoltammetry,
    'pot': TechniqueId.Chronopotentiometry,
}


def _current_amp(value: AllowedCurrentRanges) -> float:
    """Convert a current-range literal such as ``'100uA'`` to amperes."""
    return cr_string_to_enum(value).Factor / 1e6


def _potential_volts(value: AllowedPotentialRanges) -> float:
    """Convert a potential-range literal such as ``'1V'`` to volts.

    NOTE: the mV divisor and the wire key names below assume the hub mirrors the
    current-range keys; confirm both against the C# models.
    """
    return pr_string_to_enum(value).Factor / 1e3


# --- shared setting groups -------------------------------------------------


def _add_current_range(p: ParamDict, rng: CurrentRange) -> None:
    p['MinimumCurrentRange'] = [_current_amp(rng.min)]
    p['MaximumCurrentRange'] = [_current_amp(rng.max)]
    p['StartingCurrentRange'] = [_current_amp(rng.start)]


def _add_potential_range(p: ParamDict, rng: PotentialRange) -> None:
    p['MinimumPotentialRange'] = [_potential_volts(rng.min)]
    p['MaximumPotentialRange'] = [_potential_volts(rng.max)]
    p['StartingPotentialRange'] = [_potential_volts(rng.start)]


def _add_pretreatment(p: ParamDict, pre: Pretreatment) -> None:
    p['ConditioningPotential'] = [pre.conditioning_potential]
    p['ConditioningTime'] = [pre.conditioning_time]
    p['DepositionPotential'] = [pre.deposition_potential]
    p['DepositionTime'] = [pre.deposition_time]


def _add_limits(p: ParamDict, kind: str, minimum: float | None, maximum: float | None) -> None:
    """Emit a Use/value limit pair for current, potential, or charge limits."""
    p[f'UseMinimum{kind}Limit'] = [minimum is not None]
    p[f'UseMaximum{kind}Limit'] = [maximum is not None]
    if minimum is not None:
        p[f'Minimum{kind}Limit'] = [minimum]
    if maximum is not None:
        p[f'Maximum{kind}Limit'] = [maximum]


def _add_ir_drop_compensation(p: ParamDict, ir: IrDropCompensation) -> None:
    # The C# mapper omits these keys entirely when no resistance is configured.
    if ir.resistance is not None:
        p['UseIRCompensation'] = [True]
        p['IRCompensation'] = [ir.resistance]


def _add_post_measurement(p: ParamDict, pm: PostMeasurement) -> None:
    if pm.cell_on_after_measurement:
        p['CellModeAfterMeasurement'] = ['CellModeAfterMeasurementPotentiostatic']
        p['UsePotentialAfterMeasurement'] = [True]
        p['PotentialAfterMeasurement'] = [pm.standby_potential]
        p['UseCurrentAfterMeasurement'] = [False]
        p['UseMeasuredCurrentRangeAfterMeasurement'] = [False]
        p['UseMeasuredPotentialRangeAfterMeasurement'] = [False]
    else:
        p['CellModeAfterMeasurement'] = ['CellModeAfterMeasurementOff']


def _add_general(p: ParamDict, gen: General) -> None:
    """Only hardware sync maps; mains frequency lives in configure, deferred."""
    p['EnableHardwareSync'] = [gen.use_hardware_sync]
    if gen.save_on_internal_storage:
        raise NotImplementedError("Lablink does not yet support 'save_on_internal_storage'")
    if gen.notes:
        raise NotImplementedError("Lablink does not yet support 'notes'")


def _require_default(name: str, value: object, default: object) -> None:
    """Raise if a still-unsupported setting differs from its default."""
    if value != default:
        raise NotImplementedError(f'Lablink does not yet support {name!r}')


# --- technique builders ----------------------------------------------------


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

    p['EquilibrationTime'] = [m.equilibration_time]
    p['IntervalTime'] = [m.interval_time]
    p['Potential'] = [m.potential]
    p['RunTime'] = [m.run_time]

    # Chronoamperometry only supports 'potential' versus OCP.
    p['PotentialOCP'] = ['potential' in m.versus_ocp.potentials]

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    _add_limits(p, 'Charge', m.charge_limits.min, m.charge_limits.max)
    _add_limits(p, 'Temperature', None, None)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = [m.record_auxiliary_input]
    p['MeasureCellPotential'] = [m.record_cell_potential]
    p['MeasureWEPotential'] = [m.record_we_potential]

    p['EnableDropDetection'] = [False]

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

    p['Current'] = [m.current]
    p['AppliedCurrentRange'] = [_current_amp(m.applied_current_range)]
    p['IntervalTime'] = [m.interval_time]
    p['RunTime'] = [m.run_time]

    _add_limits(p, 'Potential', m.potential_limits.min, m.potential_limits.max)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = [m.record_auxiliary_input]
    p['MeasureCellPotential'] = [m.record_cell_potential]
    p['MeasureWECurrent'] = [m.record_we_current]

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

    p['EquilibrationTime'] = [m.equilibration_time]
    p['BeginPotential'] = [m.begin_potential]
    p['Vertex1Potential'] = [m.vertex1_potential]
    p['Vertex2Potential'] = [m.vertex2_potential]
    p['StepPotential'] = [m.step_potential]
    p['ScanRate'] = [m.scanrate]
    p['NumberOfScans'] = [m.n_scans]

    # CV OCP is per-potential, not a shared EnableOCP flag.
    p['BeginPotentialOCP'] = ['begin' in m.versus_ocp.potentials]
    p['Vertex1PotentialOCP'] = ['vertex1' in m.versus_ocp.potentials]
    p['Vertex2PotentialOCP'] = ['vertex2' in m.versus_ocp.potentials]

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    # CV has no charge/temperature limit fields; the hub still expects the flags.
    _add_limits(p, 'Charge', None, None)
    _add_limits(p, 'Temperature', None, None)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = [m.record_auxiliary_input]
    p['MeasureCellPotential'] = [m.record_cell_potential]
    p['MeasureWEPotential'] = [m.record_we_potential]

    p['EnableDropDetection'] = [False]

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

    p['EquilibrationTime'] = [m.equilibration_time]
    p['BeginPotential'] = [m.begin_potential]
    p['EndPotential'] = [m.end_potential]
    p['StepPotential'] = [m.step_potential]
    p['ScanRate'] = [m.scanrate]

    # LSV OCP is per-potential (begin/end), not a shared EnableOCP flag.
    p['BeginPotentialOCP'] = ['begin' in m.versus_ocp.potentials]
    p['EndPotentialOCP'] = ['end' in m.versus_ocp.potentials]

    _add_limits(p, 'Current', m.current_limits.min, m.current_limits.max)
    _add_limits(p, 'Charge', None, None)
    _add_limits(p, 'Temperature', None, None)
    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureAuxiliaryInput'] = [m.record_auxiliary_input]
    p['MeasureCellPotential'] = [m.record_cell_potential]
    p['MeasureWEPotential'] = [m.record_we_potential]

    p['EnableDropDetection'] = [False]

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

    p['EquilibrationTime'] = [m.equilibration_time]
    p['BeginPotential'] = [m.begin_potential]
    p['EndPotential'] = [m.end_potential]
    p['StepPotential'] = [m.step_potential]
    p['Frequency'] = [m.frequency]
    p['Amplitude'] = [m.amplitude]

    p['BeginPotentialOCP'] = ['begin' in m.versus_ocp.potentials]
    p['EndPotentialOCP'] = ['end' in m.versus_ocp.potentials]

    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['MeasureCurrentForwardReverse'] = [m.record_forward_and_reverse_currents]
    p['EnableDropDetection'] = [False]

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

    p['EquilibrationTime'] = [m.equilibration_time]
    p['BeginPotential'] = [m.begin_potential]
    p['EndPotential'] = [m.end_potential]
    p['StepPotential'] = [m.step_potential]
    p['PulsePotential'] = [m.pulse_potential]
    p['PulseTime'] = [m.pulse_time]
    p['ScanRate'] = [m.scan_rate]

    p['BeginPotentialOCP'] = ['begin' in m.versus_ocp.potentials]
    p['EndPotentialOCP'] = ['end' in m.versus_ocp.potentials]

    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = [False]

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

    p['EquilibrationTime'] = [m.equilibration_time]
    p['BeginPotential'] = [m.begin_potential]
    p['EndPotential'] = [m.end_potential]
    p['StepPotential'] = [m.step_potential]
    p['PulseTime'] = [m.pulse_time]
    p['ScanRate'] = [m.scan_rate]

    p['BeginPotentialOCP'] = ['begin' in m.versus_ocp.potentials]
    p['EndPotentialOCP'] = ['end' in m.versus_ocp.potentials]

    _add_ir_drop_compensation(p, m.ir_drop_compensation)
    _add_post_measurement(p, m.post_measurement)

    p['EnableDropDetection'] = [False]

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
}


def _to_parameters(method: MethodTypeCompatible) -> ParamDict:
    """Build the decoded parameter dict for a technique."""
    builder = _BUILDERS.get(method.id)
    if builder is None:
        raise NotImplementedError(f'Lablink does not support technique id {method.id!r}')

    params = builder(method)
    params['Name'] = [ID_TO_TECHNIQUE[method.id].value]
    return params


def to_payload(method: MethodTypeCompatible) -> dict[str, object]:
    """Build the ``StartMeasurementCommand`` body for a technique.

    Values are JSON-encoded so the result is the wire ``dict[str, str]`` the hub
    expects (``MethodParameters``); ``Technique`` carries the technique name.
    """
    params = _to_parameters(method)
    return {
        'Technique': ID_TO_TECHNIQUE[method.id].value,
        'MethodParameters': {key: json.dumps(value) for key, value in params.items()},
    }
