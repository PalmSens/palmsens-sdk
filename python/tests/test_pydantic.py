from __future__ import annotations

from typing import Any, ClassVar

import PalmSens
from pydantic import BaseModel

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
    cv = ps.CyclicVoltammetry(
        current_range={
            'min': ps.settings.CURRENT_RANGE.cr_10_uA,
            'max': ps.settings.CURRENT_RANGE.cr_10_mA,
            'start': ps.settings.CURRENT_RANGE.cr_1_mA,
        }
    )

    assert isinstance(cv.current_range, ps.settings.CurrentRange)
    assert cv.current_range.min.name == 'cr_10_uA'
    assert cv.current_range.max.name == 'cr_10_mA'
    assert cv.current_range.start.name == 'cr_1_mA'

    m = cv._to_psmethod()

    assert m.Ranging.MinimumCurrentRange.ToString() == '10 uA'
    assert m.Ranging.MaximumCurrentRange.ToString() == '10 mA'
    assert m.Ranging.StartCurrentRange.ToString() == '1 mA'
