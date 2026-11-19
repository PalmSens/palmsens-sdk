from __future__ import annotations

import pytest

import pypalmsens as ps
from pypalmsens._data import Method
from pypalmsens._methods.adapters import technique_adapter


@pytest.fixture
def method(measurement_cv_1scan):
    return Method._wrap(measurement_cv_1scan._inner.Method)


def test_method_init_fail():
    with pytest.raises(TypeError):
        _ = Method()


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

    method = ps.MethodScript(script='send_string "Test"\n')
    method.to_file(path)
    method2 = ps.MethodScript().from_file(path)

    assert method2.script == method.script
    assert method2 == method


def test_structure_unstructure():
    data = technique_adapter.validate_python({'id': 'cv'})
    assert isinstance(data, ps.CyclicVoltammetry)

    data = technique_adapter.validate_python({'id': 'eis'})
    assert isinstance(data, ps.ElectrochemicalImpedanceSpectroscopy)


def test_method_capabilities_errors_ms():
    method = ps.MethodScript()
    assert method.supports('emstat4hr')
    assert not method.supports('palmsens4')


def test_method_capabilities_errors_ca():
    method = ps.ChronoAmperometry()

    assert len(method.capability_errors('emstat4hr')) == 0
    assert method.supports('emstat4hr')

    method.current_range.min = '100pA'
    assert len(method.capability_errors('emstat4hr')) == 1
    assert not method.supports('emstat4hr')


@pytest.mark.xfail(reason='https://github.com/PalmSens/palmsens-sdk/issues/522')
def test_method_capabilities_errors_bipot():
    method = ps.ChronoAmperometry()

    method.enable_bipot_current = True
    method.bipot.current_range = {'min': '1uA', 'max': '1mA', 'start': '10uA'}

    # emstat4 does not support bipot autoranging
    assert len(method.capability_errors('emstat4hr')) > 0
    assert not method.supports('emstat4hr')
