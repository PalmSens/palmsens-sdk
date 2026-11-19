from __future__ import annotations

import logging
from typing import Any

import pytest

import pypalmsens as ps
from pypalmsens._methods.adapters import (
    energy_technique_adapter,
)
from pypalmsens._methods.energy import BaseMethodScriptTechnique

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instrument, *_ = ps.discover()
    with ps.connect(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield mgr


class BCY:
    """Note: requires dummy circuit or method will hang."""

    kwargs = {
        'id': 'bcy',
        'cycles': 1,
        'max_time': 1,
        'cell_on_ocp': False,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        expected_curves: list[dict[str, Any]] = [
            {'x': 'Time', 'y': 'Potential', 'min_len': 4},
            {'x': 'Time', 'y': 'Current', 'min_len': 4},
            {'x': 'Cycle', 'y': 'Passed Q', 'min_len': 1},
            {'x': 'Cycle', 'y': 'Passed Q', 'min_len': 1},
        ]

        curves = measurement.curves

        assert len(curves) == len(expected_curves)  # 2 + cycles * 2 ?

        for curve, expected in zip(measurement.curves, expected_curves):
            assert curve.x_label == expected['x']
            assert curve.y_label == expected['y']
            assert len(curve) >= expected['min_len']

        dataset = measurement.dataset

        assert len(dataset) == 6

        assert dataset.array_names == {
            'AnalogInput01_2',
            'AnalogInput02_2',
            'AnalogInput11_2',
            'AppliedCurrent1_2',
            'Potential1_2',
            'Time1_2',
        }
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Passed Q', 'Cycle'}


class DCP:
    """Note: requires dummy circuit."""

    kwargs = {
        'id': 'dcp',
        'duration': 0.2,
        'interval': 0.01,
        'cell_on_ocp': False,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        assert measurement.title == 'Constant Power'

        curves = measurement.curves

        assert len(curves) == 2

        for curve in curves:
            assert len(curve) == 2

        dataset = measurement.dataset

        assert dataset.array_names == {'AppliedCurrent1_2', 'Potential1_2', 'Time1_2'}
        assert dataset.array_quantities == {'Time', 'Potential', 'Current'}


class DCR:
    """Note: requires dummy circuit."""

    kwargs = {
        'id': 'dcr',
        'duration': 0.2,
        'cell_on_ocp': False,
        'cutoff': 0,
        'interval': 0.01,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        assert measurement.title == 'Constant Resistance'

        curves = measurement.curves

        assert len(curves) == 2

        for curve in curves:
            assert len(curve) > 0

        dataset = measurement.dataset

        assert dataset.array_names == {'AppliedCurrent1_2', 'Potential1_2', 'Time1_2'}
        assert dataset.array_quantities == {'Time', 'Potential', 'Current'}


@pytest.mark.parametrize(
    'method',
    (
        BCY,
        DCP,
        pytest.param(DCR, marks=pytest.mark.flaky),
    ),
)
def test_measure(manager, method):

    params = energy_technique_adapter.validate_python(method.kwargs)

    assert isinstance(params, BaseMethodScriptTechnique)

    measurement = manager.measure(params)
    method.validate(measurement)
