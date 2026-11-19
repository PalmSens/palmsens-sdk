"""Regression: the DLL-free mapper must reproduce the DLL-produced mapping.

The baseline in `data/lablink_expected_mapping.json` is generated from the C#
`TechniqueParametersMappers` (see `lablink/gen_expected_mapping.py`) and
committed, so this test needs no DLL: it rebuilds each method from the stored
`spec` and diffs `_to_parameters` output against the `expected` mapping.
Re-run the generator after any C# model change to refresh the baseline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pypalmsens.lablink.models._method_mapper import (
    _BUILDERS,
    _GroupValue,
    _RawWireValue,
    _to_parameters,
)

from .test_method_mapper import _BY_ID

FIXTURE = Path(__file__).parent / 'data' / 'lablink_expected_mapping.json'
_DATA = json.loads(FIXTURE.read_text())

_BUILT = sorted(set(_DATA) & set(_BUILDERS))


def _norm(value: object) -> object:
    """Normalise numeric leaves so C# `0` and Python `0.0` compare equal."""
    if isinstance(value, (_RawWireValue, _GroupValue)):
        return float(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        return {key: _norm(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_norm(item) for item in value]
    return value


@pytest.mark.parametrize(
    'method_id, variant',
    [(method_id, variant) for method_id in _BUILT for variant in ('default', 'extended')],
)
def test_matches_dll_mapping(method_id: str, variant: str) -> None:
    import deepdiff

    entry = _DATA[method_id][variant]
    method = _BY_ID[method_id].from_dict(entry['spec'])

    try:
        ours = dict(_to_parameters(method))
    except NotImplementedError as exc:
        pytest.skip(f'{method_id}/{variant} is guarded: {exc}')
    ours.pop('Name', None)

    result = deepdiff.DeepDiff(_norm(entry['expected']), _norm(ours), ignore_order=True)

    assert not result, f'{method_id}/{variant}: {result}'
