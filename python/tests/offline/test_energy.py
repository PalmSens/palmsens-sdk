from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import pytest

import pypalmsens as ps
from pypalmsens._methods.adapters import (
    energy_technique_adapter,
)
from pypalmsens._methodscript import validate as validate_methodscript
from pypalmsens.energy import (
    experimental_BatteryCycling,
    experimental_ConstantPower,
    experimental_ConstantResistance,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instrument, *_ = ps.discover()
    with ps.connect(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
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
    kwargs = {
        'id': 'bcy',
        'cycles': 1,
        'max_time': 1,
        'cell_on_ocp': False,
    }


class DCP:
    kwargs = {
        'id': 'dcp',
        'duration': 0.2,
        'interval': 0.01,
        'cell_on_ocp': False,
    }


class DCR:
    kwargs = {
        'id': 'dcr',
        'duration': 0.2,
        'cell_on_ocp': False,
        'cutoff': 0,
        'interval': 0.01,
    }


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
