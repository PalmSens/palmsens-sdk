from __future__ import annotations

import pytest

import pypalmsens as ps


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
    assert isinstance(params, ps.CyclicVoltammetry)


def test_methodscript_file_roundtrip(tmpdir):
    path = tmpdir / 'test.mscr'

    method = ps.MethodScript(script='e\nsend_string "Test"\n\n')
    method.to_file(path)
    method2 = ps.MethodScript().from_file(path)

    assert method2.script == method.script
    assert method2 == method
