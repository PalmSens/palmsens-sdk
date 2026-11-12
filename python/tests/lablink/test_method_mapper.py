from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import pytest

from pypalmsens._methods import BaseTechnique
from pypalmsens.lablink.models._method_mapper import _BUILDERS, ID_TO_TECHNIQUE, to_payload

if TYPE_CHECKING:
    from pypalmsens._types import MethodTypeCompatible

IMPLEMENTED = sorted(_BUILDERS)


def make(method_id: str, **kwargs: object):
    """Build a concrete technique by id, defaulting any field not passed."""
    return BaseTechnique._registry[method_id](**kwargs)


def _params(method: MethodTypeCompatible) -> dict[str, list[float | bool | str]]:
    """Decoded parameter dict (the level the builders return, before encoding)."""
    from pypalmsens.lablink.models._method_mapper import _to_parameters

    return _to_parameters(method)


@pytest.mark.parametrize('method_id', IMPLEMENTED)
def test_to_payload_shape(method_id: str) -> None:
    payload = to_payload(make(method_id))

    assert payload['Technique'] == ID_TO_TECHNIQUE[method_id].value
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert all(isinstance(value, str) for value in params.values())
    assert all(isinstance(json.loads(value), list) for value in params.values())

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


@pytest.mark.parametrize('method_id', IMPLEMENTED)
def test_guard_general_notes(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, general={'notes': 'not supported yet'}))


@pytest.mark.parametrize('method_id', IMPLEMENTED)
def test_guard_general_save_on_internal_storage(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, general={'save_on_internal_storage': True}))


@pytest.mark.parametrize('method_id', IMPLEMENTED)
def test_guard_data_processing(method_id: str) -> None:
    with pytest.raises(NotImplementedError):
        _ = _params(make(method_id, data_processing={'smooth_level': 2}))
