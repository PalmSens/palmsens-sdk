from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import pytest

from pypalmsens._methods import BaseTechnique
from pypalmsens.lablink.models._method_mapper import _BUILDERS, ID_TO_TECHNIQUE, to_payload

if TYPE_CHECKING:
    from pydantic import BaseModel

    from pypalmsens._types import MethodTypeCompatible

IMPLEMENTED = sorted(_BUILDERS)


def model_class(method_id: str) -> type[BaseModel]:
    """The technique class for an id.

    `BaseTechnique._registry` is typed as `type[MethodType]`, which does not declare the
    pydantic attributes these tests introspect, so it is widened here rather than at every use.
    """
    return cast('type[BaseModel]', BaseTechnique._registry[method_id])


def has_field(method_id: str, field: str) -> bool:
    """Whether the technique model exposes a settings field at all."""
    return field in model_class(method_id).model_fields


# MethodScript is just a script: it has no `general` or `data_processing` to guard.
WITH_GENERAL = [method_id for method_id in IMPLEMENTED if has_field(method_id, 'general')]
WITH_DATA_PROCESSING = [
    method_id for method_id in IMPLEMENTED if has_field(method_id, 'data_processing')
]


def make(method_id: str, **kwargs: object):
    """Build a concrete technique by id, defaulting any field not passed."""
    return BaseTechnique._registry[method_id](**kwargs)


def _params(method: MethodTypeCompatible) -> dict[str, float | bool | str]:
    """Decoded parameter dict (the level the builders return, before encoding)."""
    from pypalmsens.lablink.models._method_mapper import _to_parameters

    return _to_parameters(method)


@pytest.mark.parametrize('method_id', IMPLEMENTED)
def test_to_payload_shape(method_id: str) -> None:
    payload = to_payload(make(method_id))

    assert payload['Technique'] == ID_TO_TECHNIQUE[method_id].value
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert all(isinstance(value, str) for value in params.values())
    # Group counts are the only values C# writes bare; everything else is a JSON array.
    assert all(
        isinstance(json.loads(value), int if key in {'Levels', 'Stages', 'Curves'} else list)
        for key, value in params.items()
    )

    # `Name` is stamped from ID_TO_TECHNIQUE and matches the Technique field.
    assert json.loads(params['Name']) == [ID_TO_TECHNIQUE[method_id].value]


def test_current_range_conversion() -> None:
    params = _params(make('ad', current_range='100uA'))
    assert params['MinimumCurrentRange'] == '0.000100'
    assert params['MaximumCurrentRange'] == '0.000100'
    assert params['StartingCurrentRange'] == '0.000100'


def test_potential_range_conversion() -> None:
    params = _params(make('pot', potential_range={'min': '10mV', 'max': '1V', 'start': '1V'}))
    assert params['MinimumPotentialRange'] == '0.010'
    assert params['MaximumPotentialRange'] == '1'
    assert params['StartingPotentialRange'] == '1'


def test_fastamperometry_fixes_one_range() -> None:
    # Fast amperometry cannot auto-range, so one literal fills min, maximum and start.
    params = _params(make('fam', current_range='100nA'))
    assert params['MinimumCurrentRange'] == '0.000000100'
    assert params['MaximumCurrentRange'] == '0.000000100'
    assert params['StartingCurrentRange'] == '0.000000100'


def test_stripping_omits_hardware_sync() -> None:
    # The C# stripping mapper leaves `EnableHardwareSync` out instead of writing false.
    assert 'EnableHardwareSync' not in _params(make('scp'))


@pytest.mark.parametrize('method_id', ['eis', 'gis'])
def test_impedance_omits_hardware_sync(method_id: str) -> None:
    # Neither impedance record carries a hardware-sync field, so the key is absent rather
    # than false (unlike every technique that goes through `_add_general`).
    assert 'EnableHardwareSync' not in _params(make(method_id))


@pytest.mark.parametrize('method_id', ['eis', 'gis'])
def test_impedance_emits_no_measure_or_scan_type_keys(method_id: str) -> None:
    # The impedance mappers write no `Measure*`, iR, `EISScanType` or `EISFrequencyType`
    # keys, even though pypalmsens exposes recording flags on both techniques.
    params = _params(make(method_id))
    assert not [key for key in params if key.startswith('Measure')]
    assert 'UseIRCompensation' not in params
    assert 'EISScanType' not in params
    assert 'EISFrequencyType' not in params


def test_eis_frequencies_per_decade_is_recomputed() -> None:
    # `NumberOfFrequenciesPerDecade` is a computed property on the C# record rather than a
    # legacy field: `(n - 1) / (log10(max) - log10(min))`, kept at seven significant digits
    # because that is all the wire carries for a value nothing stores verbatim.
    params = _params(make('eis', n_frequencies=21, max_frequency=1e4, min_frequency=10.0))
    assert params['NumberOfFrequencies'] == 21
    assert params['NumberOfFrequenciesPerDecade'] == 6.666667

    with pytest.raises(NotImplementedError):
        # An empty frequency range divides by zero; C# writes `NaN` there, which no parser
        # can read back.
        _ = _params(make('eis', max_frequency=1e3, min_frequency=1e3))


def test_eis_dc_potential_versus_ocp() -> None:
    # A fixed scan type offers only the 'potential' OCP flag, i.e. OCPmode bit 0.
    params = _params(make('eis', versus_ocp={'potentials': ['potential'], 'timeout': 15.0}))
    assert params['PotentialDirectCurrentOCP'] is True
    assert params['EnableOcp'] is True
    assert params['MaximumOCPTime'] == 15.0
    assert params['OCPStabilityCriterion'] == 0.0


def test_gis_is_galvanostatic_only() -> None:
    params = _params(make('gis', applied_current_range='1mA', dc_current=0.2, ac_current=0.05))
    assert params['AppliedCurrentRange'] == '0.001'
    assert params['DCCurrent'] == 0.2
    assert params['ACCurrent'] == 0.05
    # The GIS record implements neither `IVsOcpParameters` nor a potentiostatic dc level.
    assert 'EnableOcp' not in params
    assert 'PotentialDirectCurrent' not in params


@pytest.mark.parametrize(
    'method_id,kinds',
    [
        ('eis', ('Current', 'Charge', 'Temperature')),
        ('gis', ('Potential', 'Charge', 'Temperature')),
    ],
)
def test_impedance_limits_are_flags_only(method_id: str, kinds: tuple[str, ...]) -> None:
    # Both impedance mappers hardcode null limits, so only the `Use...` flags are written,
    # and each technique flags only the kinds its own record declares.
    params = _params(make(method_id))
    for kind in kinds:
        assert params[f'UseMinimum{kind}Limit'] is False
        assert params[f'UseMaximum{kind}Limit'] is False
        assert f'Minimum{kind}Limit' not in params
        assert f'Maximum{kind}Limit' not in params
    absent = 'Potential' if method_id == 'eis' else 'Current'
    assert f'UseMinimum{absent}Limit' not in params


@pytest.mark.parametrize('method_id', ['eis', 'gis'])
def test_guard_scan_and_frequency_type(method_id: str) -> None:
    # The domain model represents exactly one shape: a frequency scan at a fixed level. The
    # legacy mapper returns null for the rest and C# then throws, so there is nothing to copy.
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, scan_type='time', run_time=1.0))
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, frequency_type='fixed'))


@pytest.mark.parametrize('method_id', ['eis', 'gis'])
def test_guard_multiplexer(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, multiplexer={'mode': 'consecutive', 'channels': [1]}))


def test_guard_eis_material() -> None:
    # Material only feeds the corrosion-rate analysis, so it never reaches the wire.
    with pytest.raises(NotImplementedError):
        _ = _params(make('eis', material={'surface_area': 1.5}))


def test_level_count_is_written_bare() -> None:
    payload = to_payload(make('ma', levels=[{'level': 0.5, 'duration': 0.1}]))
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['Levels'] == '1'
    assert params['Levels/0/Level/Potential'] == '[0.5]'


def test_potential_range_snaps_to_supported_ranges() -> None:
    # The legacy ranging only supports 1mV/10mV/100mV/1V, snaps the other literals up, and
    # clamps the start range into the snapped window.
    params = _params(
        make('pot', potential_range={'min': '20mV', 'max': '500mV', 'start': '10mV'})
    )
    assert params['MinimumPotentialRange'] == '0.100'
    assert params['MaximumPotentialRange'] == '1'
    assert params['StartingPotentialRange'] == '0.100'

    params = _params(make('mp', potential_range={'min': '10mV', 'max': '100mV', 'start': '1V'}))
    assert params['StartingPotentialRange'] == '0.100'

    params = _params(make('ocp', potential_range={'min': '1mV', 'max': '1V', 'start': '200mV'}))
    assert params['StartingPotentialRange'] == '1'


def test_multistep_potentiometry_levels_apply_current() -> None:
    # MP levels carry an applied current with potential limits; MA carries a potential with
    # current limits. MP also writes neither iR nor charge keys.
    params = _params(
        make(
            'mp',
            levels=[{'level': 0.5, 'duration': 0.1, 'limit_potential_max': 1.0}],
            record_auxiliary_input=True,
            record_we_current=True,
        )
    )
    assert params['Levels/0/Level/AppliedCurrent'] == 0.5
    assert params['Levels/0/Level/UseMaximumPotentialLimit'] is True
    assert params['Levels/0/Level/MaximumPotentialLimit'] == 1.0
    assert 'Levels/0/Level/MinimumPotentialLimit' not in params
    assert params['SelectLimitPerLevel'] is True
    assert params['AppliedCurrentRange'] == '0.000001'
    assert params['MeasureAuxiliaryInput'] is True
    assert params['MeasureWECurrent'] is True
    assert 'UseIRCompensation' not in params
    assert 'Levels/0/Level/Potential' not in params


def test_stage_count_is_written_bare() -> None:
    payload = to_payload(
        make(
            'mm',
            stages=[
                {'stage_type': 'OpenCircuit', 'run_time': 0.1},
                {'stage_type': 'ConstantE', 'potential': 0.5, 'run_time': 0.1},
            ],
        )
    )
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['Stages'] == '2'
    assert params['Stages/0/OpenCircuitStage/RunTime'] == '[0.1]'
    assert params['Stages/1/ConstantPotentialStage/Potential'] == '[0.5]'


def test_stage_keys_nest_under_the_group_name() -> None:
    # Each stage type is nested under its own `GroupId` name, not under the pypalmsens id.
    params = _params(
        make(
            'mm',
            stages=[
                {'stage_type': 'ConstantE'},
                {'stage_type': 'ConstantI'},
                {'stage_type': 'SweepE'},
                {'stage_type': 'OpenCircuit'},
            ],
        )
    )
    groups = {key.split('/')[2] for key in params if key.startswith('Stages/')}
    assert groups == {
        'ConstantPotentialStage',
        'ConstantCurrentStage',
        'SweepPotentialStage',
        'OpenCircuitStage',
    }
    assert 'Stages/0/ConstantPotentialStage/Potential' in params
    assert 'Stages/1/ConstantCurrentStage/AppliedCurrent' in params
    assert 'Stages/2/SweepPotentialStage/ScanRate' in params
    assert 'Stages/3/OpenCircuitStage/RunTime' in params


def test_stage_versus_previous_flags_are_always_false() -> None:
    # pypalmsens has no setting that feeds the legacy `VsEiPropertiesList`, yet the stage
    # mapper writes every `…VersusPrevious` flag unconditionally, so the default is what C#
    # stores (measured against the DLL).
    params = _params(
        make(
            'mm',
            stages=[
                {'stage_type': 'ConstantE'},
                {'stage_type': 'ConstantI'},
                {'stage_type': 'SweepE'},
                {'stage_type': 'OpenCircuit'},
            ],
        )
    )
    versus_previous = [key for key in params if key.endswith('VersusPrevious')]
    assert versus_previous == [
        'Stages/0/ConstantPotentialStage/PotentialVersusPrevious',
        'Stages/1/ConstantCurrentStage/AppliedCurrentVersusPrevious',
        'Stages/2/SweepPotentialStage/BeginPotentialVersusPrevious',
        'Stages/2/SweepPotentialStage/EndPotentialVersusPrevious',
    ]
    assert all(params[key] is False for key in versus_previous)


def test_stage_limits_nest_and_follow_the_stage_kind() -> None:
    # A stage writes only the limit kinds its record declares, nested like the level limits.
    params = _params(
        make(
            'mm',
            stages=[
                {'stage_type': 'ConstantE', 'current_limits': {'min': -2.5}},
                {'stage_type': 'OpenCircuit', 'potential_limits': {'max': 0.75}},
            ],
        )
    )
    assert params['Stages/0/ConstantPotentialStage/UseMinimumCurrentLimit'] is True
    assert params['Stages/0/ConstantPotentialStage/MinimumCurrentLimit'] == -2.5
    assert params['Stages/0/ConstantPotentialStage/UseMaximumCurrentLimit'] is False
    assert 'Stages/0/ConstantPotentialStage/MaximumCurrentLimit' not in params
    assert 'Stages/0/ConstantPotentialStage/UseMinimumPotentialLimit' not in params
    assert params['Stages/1/OpenCircuitStage/UseMaximumPotentialLimit'] is True
    assert params['Stages/1/OpenCircuitStage/MaximumPotentialLimit'] == 0.75
    assert 'Stages/1/OpenCircuitStage/UseMinimumCurrentLimit' not in params


def test_mixed_mode_potential_ranges_are_the_legacy_defaults() -> None:
    # MixedMode offers no `potential_range` setting, but the domain record requires the
    # triple, so C# stores the `RangingPotential` defaults the legacy object was built with.
    assert not has_field('mm', 'potential_range')
    params = _params(make('mm'))
    assert params['MinimumPotentialRange'] == '0.001'
    assert params['MaximumPotentialRange'] == '1'
    assert params['StartingPotentialRange'] == '1'


def test_guard_mixed_mode_impedance_stage() -> None:
    # The C# stage mapper throws `Unknown stage type: MixedModeStageEIS`, so no reference
    # output exists for a method containing an impedance stage (PLAN.md §6).
    with pytest.raises(NotImplementedError):
        _ = _params(
            make(
                'mm',
                stages=[
                    {
                        'stage_type': 'Impedance',
                        'run_time': 0.2,
                        'dc_potential': 0.0,
                        'ac_potential': 0.01,
                        'min_sampling_time': 0.01,
                    }
                ],
            )
        )


def test_methodscript_sends_the_legacy_script() -> None:
    # C# stores the legacy MethodScript text, so the `e` header and trailing newline that
    # `MethodScript._export` adds must survive into the JSON-escaped value.
    payload = to_payload(make('ms', script='cell_on\n'))
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['Script'] == '["e\\ncell_on\\n\\n"]'
    assert params['Name'] == '["MethodScriptSandbox"]'
    assert set(params) == {'Name', 'Script'}


def test_wire_number_formatting() -> None:
    # C# formats doubles with `G7`: integral values print without a decimal point,
    # and magnitudes below 1e-4 fall back to E notation.
    payload = to_payload(make('ad', run_time=1.0, interval_time=1e-5, potential=1.2345678))
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['RunTime'] == '[1]'
    assert params['IntervalTime'] == '[1E-05]'
    assert params['Potential'] == '[1.234568]'
    assert params['Name'] == '["Chronoamperometry"]'
    assert params['CellModeAfterMeasurement'] == '["CellModeAfterMeasurementOff"]'


@pytest.mark.parametrize('method_id', ['ad', 'cv', 'lsv', 'swv', 'dpv', 'npv'])
def test_guard_enable_bipot_current(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, enable_bipot_current=True))


@pytest.mark.parametrize('method_id', ['swv', 'dpv', 'npv'])
def test_guard_record_auxiliary_input(method_id: str) -> None:
    # SWV/DPV/NPV emit no aux/cell/WE keys, so a set flag must raise.
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, record_auxiliary_input=True))


@pytest.mark.parametrize('method_id', WITH_GENERAL)
def test_guard_general_notes(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, general={'notes': 'not supported yet'}))


@pytest.mark.parametrize('method_id', WITH_GENERAL)
def test_guard_general_save_on_internal_storage(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, general={'save_on_internal_storage': True}))


@pytest.mark.parametrize('method_id', WITH_DATA_PROCESSING)
def test_guard_data_processing(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, data_processing={'smooth_level': 2}))
