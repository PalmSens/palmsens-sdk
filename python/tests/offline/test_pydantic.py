from __future__ import annotations

from typing import Any, ClassVar

import PalmSens
import pytest
from pydantic import BaseModel, ValidationError

import pypalmsens as ps


def test_registry():
    class Model(BaseModel, extra='forbid'):
        _registry: ClassVar[dict[str, object]] = {}
        id: ClassVar[str]

        def __init_subclass__(cls, **kwargs: Any):
            super().__init_subclass__(**kwargs)
            cls._registry[cls.id] = cls

    class SubModel(Model):
        id: ClassVar[str] = 'foo'

    assert len(Model._registry) == 1
    assert 'foo' in Model._registry
    assert Model._registry['foo'] == SubModel


def test_id():
    cv = ps.CyclicVoltammetry()

    assert cv.id == 'cv'

    m = cv._to_psmethod()

    assert isinstance(m, PalmSens.Method)
    assert m.MethodID == 'cv'


def test_validation():
    cr_dict = {
        'min': '10uA',
        'max': '10mA',
        'start': '1mA',
    }

    cv = ps.CyclicVoltammetry(current_range=cr_dict)

    assert isinstance(cv.current_range, ps.settings.CurrentRange)
    assert cv.current_range.min == '10uA'
    assert cv.current_range.max == '10mA'
    assert cv.current_range.start == '1mA'

    m = cv._to_psmethod()

    assert str(m.Ranging.MinimumCurrentRange) == '10 uA'
    assert str(m.Ranging.MaximumCurrentRange) == '10 mA'
    assert str(m.Ranging.StartCurrentRange) == '1 mA'


def test_wrong_value():
    cv = ps.CyclicVoltammetry()
    with pytest.raises(ValidationError):
        cv.current_range.min = 'fail'
