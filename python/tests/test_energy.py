from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

import pytest

import pypalmsens as ps
from pypalmsens._methods.adapters import (
    energy_technique_adapter,
)
from pypalmsens._methods.energy import BaseMethodScriptTechnique
from pypalmsens._methodscript import validate as validate_methodscript
from pypalmsens.energy import (
    experimental_BatteryCycling,
    experimental_ConstantPower,
    experimental_ConstantResistance,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instruments = ps.discover()
    with ps.connect(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield mgr


@pytest.mark.parametrize(
    'cls',
    (
        experimental_BatteryCycling,
        experimental_ConstantPower,
        experimental_ConstantResistance,
    ),
)
def test_render(cls):
    method = cls()
    validate_methodscript(method.render())


class BCY:
    """Note: requires dummy circuit."""

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
        'duration': 3,
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
        'duration': 1,
        'cell_on_ocp': False,
        'cutoff': 0,
        'interval': 0.1,
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


@pytest.mark.instrument
@pytest.mark.parametrize(
    'method',
    (
        BCY,
        DCP,
        DCR,
    ),
)
def test_measure(manager, method):

    params = energy_technique_adapter.validate_python(method.kwargs)

    assert isinstance(params, BaseMethodScriptTechnique)

    measurement = manager.measure(params)
    method.validate(measurement)


@pytest.mark.parametrize(
    'method',
    (
        BCY,
        DCP,
        DCR,
    ),
)
def test_params_round_trip(method):
    params = energy_technique_adapter.validate_python(method.kwargs)

    ms_params = params.to_methodscript()

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, f'{params.id}.psmethod')
        ps.save_method_file(path, ms_params)
        new_params = ps.load_method_file(path)

    # skip header/timestamp
    assert new_params.script.splitlines()[3:] == params.render().splitlines()[3:]


def test_battery_cycling_convert_values():
    m = ps.energy.experimental_BatteryCycling()
    script = m.render().splitlines()[33:45]

    assert script == [
        'store_var cycle 1i ja # first cycle',
        'store_var potential_max 4300m ab',
        'store_var current_min 5u ba',
        'store_var potential_min 2500m ab',
        'store_var current_charge 100u ba',
        'store_var current_discharge -100u ba',
        'store_var cycles 100i ja',
        'store_var interval 100m eb',
        'store_var max_time 3 eb',
        'store_var delta_v 100u ia',
        'store_var delta_i 500n ha',
        'store_var delta_t 100m eb',
    ]


def test_constant_resistance_convert_values():
    m = ps.energy.experimental_ConstantResistance()
    script = m.render().splitlines()[14:18]

    assert script == [
        'store_var load -80 db',
        'store_var cutoff 2500m ab',
        'store_var duration 3600 eb',
        'store_var interval 1 eb',
    ]


def test_constant_power_convert_values():
    m = ps.energy.experimental_ConstantPower()
    script = m.render().splitlines()[14:18]

    assert script == [
        'store_var power -200m db',
        'store_var cutoff 2500m ab',
        'store_var duration 3600 eb',
        'store_var interval 1 eb',
    ]
