from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import pytest

from pypalmsens._methods import BaseTechnique
from pypalmsens.lablink.models._method_mapper import _BUILDERS, ID_TO_TECHNIQUE, to_payload

if TYPE_CHECKING:
    from pypalmsens._types import MethodTypeCompatible

IMPLEMENTED = sorted(_BUILDERS)


def has_field(method_id: str, field: str) -> bool:
    """Whether the technique model exposes a settings field at all."""
    return field in BaseTechnique._registry[method_id].model_fields


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
