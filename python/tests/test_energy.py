from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

import pypalmsens as ps
from pypalmsens._methods.adapters import (
    energy_technique_adapter,
)
from pypalmsens.energy import experimental_BatteryCycling

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instruments = ps.discover()
    with ps.connect(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield mgr


def test_float_gives_error():
    with pytest.raises(ValidationError):
        _ = experimental_BatteryCycling(max_time=1.123)


class BC:
    """Note: requires dummy circuit."""

    kwargs = {
        'id': 'bc',
        'cycles': 1,
        'max_time': 1,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        expected_curves: list[dict[str, Any]] = [
            {'x': 'Time', 'y': 'Potential', 'min_len': 6},
            {'x': 'Time', 'y': 'Current', 'min_len': 6},
            {'x': 'Potential', 'y': 'Potential', 'min_len': 1},
            {'x': 'Potential', 'y': 'Potential', 'min_len': 1},
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
        assert dataset.array_quantities == {'Current', 'Potential', 'Time'}


@pytest.mark.instrument
@pytest.mark.parametrize(
    'method',
    (BC,),
)
def test_measure(manager, method):
    params = energy_technique_adapter.validate_python(method.kwargs)

    assert isinstance(params, experimental_BatteryCycling)

    measurement = manager.measure(params)
    method.validate(measurement)


@pytest.mark.parametrize(
    'method',
    (BC,),
)
def test_params_round_trip(method):
    params = energy_technique_adapter.validate_python(method.kwargs)
    ms_params = params.to_methodscript()

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, f'{params.id}.psmethod')
        ps.save_method_file(path, ms_params)
        new_params = ps.load_method_file(path)

    # Skip header
    assert new_params.script.splitlines()[4:] == params.render().splitlines()[4:]
