from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from helpers.technique_specs import TECHNIQUE_SPECS
from pydantic import ValidationError

import pypalmsens as ps
from pypalmsens._methods import BaseTechnique


def test_forbid_extra_keys():
    with pytest.raises(ValidationError):
        _ = ps.CyclicVoltammetry(foo=123, bar=678)


@pytest.mark.parametrize('variant', TECHNIQUE_SPECS)
def test_params_round_trip(variant):
    spec = TECHNIQUE_SPECS[variant]
    params = BaseTechnique._registry[spec.id].from_dict(spec.kwargs)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, f'{spec.id}.psmethod')
        ps.save_method_file(path, params)
        new_params = ps.load_method_file(path)

    assert new_params == params
