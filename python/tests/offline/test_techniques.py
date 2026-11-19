from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from helpers.technique_specs import TECHNIQUE_SPECS
from pydantic import ValidationError

import pypalmsens as ps


def test_forbid_extra_keys():
    with pytest.raises(ValidationError):
        _ = ps.CyclicVoltammetry(foo=123, bar=678)


@pytest.mark.parametrize('variant', TECHNIQUE_SPECS)
def test_params_round_trip(variant: str):
    method = TECHNIQUE_SPECS[variant]

    # dict-level round trip
    assert method.from_dict(method.to_dict()) == method

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, f'{method.id}.psmethod')
        ps.save_method_file(path, method)
        new_method = ps.load_method_file(path)

    assert new_method == method
