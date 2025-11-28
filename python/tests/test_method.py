from __future__ import annotations

import pytest

import pypalmsens


@pytest.fixture
def method(data_cv_1scan):
    return data_cv_1scan[0].method


def test_properties(method):
    assert isinstance(repr(method), str)
    assert method.id == 'cv'
    assert method.name == 'Cyclic Voltammetry'
    assert method.short_name == 'CV'
    assert method.technique_number == 5


def test_to_dict(method):
    dct = method.to_dict()
    assert dct


def test_to_settings(method):
    params = method.to_settings()
    assert isinstance(params, pypalmsens.CyclicVoltammetry)
