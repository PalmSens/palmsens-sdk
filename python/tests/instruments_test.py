import logging

import pytest
from PalmSens.Techniques import CyclicVoltammetry as PSCyclicVoltammetry
from PalmSens.Techniques import LinearSweep as PSLinearSweep
from PalmSens.Techniques import OpenCircuitPotentiometry as PSOpenCircuitPotentiometry
from PalmSens.Techniques import Potentiometry as PSPotentiometry
from PalmSens.Techniques import SquareWave as PSSquareWave

from pspython import pspyinstruments
from pspython.data.measurement import Measurement
from pspython.methods._shared import get_current_range, get_potential_range
from pspython.methods.cyclic_voltammetry import CyclicVoltammetryParameters, cyclic_voltammetry
from pspython.methods.linear_sweep import LinearSweepParameters, linear_sweep_voltammetry
from pspython.methods.open_circuit_potentiometry import (
    OpenCircuitPotentiometryParameters,
    open_circuit_potentiometry,
)
from pspython.methods.potentiometry import (
    PotentiometryParameters,
    chronopotentiometry,
)
from pspython.methods.squarewave import SquareWaveParameters, square_wave_voltammetry

logger = logging.getLogger(__name__)


pytestmark = pytest.mark.instrument


@pytest.fixture(scope='module')
def manager():
    mgr = pspyinstruments.InstrumentManager()

    available_instruments = pspyinstruments.discover_instruments()
    logger.warning('Connecting to %s' % available_instruments[0].name)
    success = mgr.connect(available_instruments[0])
    assert success

    yield mgr

    success = mgr.disconnect()
    assert success


def test_get_instrument_serial(manager):
    val = manager.get_instrument_serial()
    assert val
    assert isinstance(val, str)


def test_read_current(manager):
    val = manager.read_current()
    assert val
    assert isinstance(val, float)


def test_read_potential(manager):
    val = manager.read_current()
    assert val
    assert isinstance(val, float)


def test_method_limits():
    kwargs = {
        'use_limit_current_max': True,
        'limit_current_max': 2.0,
        'use_limit_current_min': True,
        'limit_current_min': 1.0,
    }

    method = CyclicVoltammetryParameters(**kwargs)
    obj = method.to_dotnet_method()

    assert obj.LimitMinValue == 1.0
    assert obj.LimitMaxValue == 2.0
    assert obj.UseLimitMinValue is True
    assert obj.UseLimitMaxValue is True


def test_method_current_range():
    crmin = get_current_range(3)
    crmax = get_current_range(7)
    crstart = get_current_range(6)

    method = CyclicVoltammetryParameters(
        current_range_min=crmin,
        current_range_max=crmax,
        current_range_start=crstart,
    )
    obj = method.to_dotnet_method()

    supported_ranges = obj.Ranging.SupportedCurrentRanges

    assert crmin in supported_ranges
    assert crmax in supported_ranges
    assert crstart in supported_ranges

    assert obj.Ranging.MinimumCurrentRange.Description == '100 nA'
    assert obj.Ranging.MaximumCurrentRange.Description == '1 mA'
    assert obj.Ranging.StartCurrentRange.Description == '100 uA'


def test_method_potential_range():
    potmin = get_potential_range(0)
    potmax = get_potential_range(4)
    potstart = get_potential_range(1)

    method = PotentiometryParameters(
        potential_range_min=potmin,
        potential_range_max=potmax,
        potential_range_start=potstart,
    )
    obj = method.to_dotnet_method()
    supported_ranges = obj.RangingPotential.SupportedPotentialRanges

    assert potmin in supported_ranges
    assert potmax in supported_ranges
    assert potstart in supported_ranges

    assert obj.RangingPotential.MinimumPotentialRange.Description == '1 mV'
    assert obj.RangingPotential.MaximumPotentialRange.Description == '100 mV'
    assert obj.RangingPotential.StartPotentialRange.Description == '10 mV'


def test_cv(manager):
    kwargs = {
        'current_range_max': get_current_range(30),
        'current_range_min': get_current_range(4),
        'current_range_start': get_current_range(8),
        'begin_potential': -1,
        'vertex1_potential': -1,
        'vertex2_potential': 1,
        'step_potential': 0.25,
        'scanrate': 5,
        'n_scans': 2,
    }
    method_old = cyclic_voltammetry(**kwargs)
    assert isinstance(method_old, PSCyclicVoltammetry)

    method = CyclicVoltammetryParameters(**kwargs)
    measurement = manager.measure(method.to_dotnet_method())

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 2

    dataset = measurement.dataset
    assert len(dataset) == 7
    assert dataset.array_names == {'scan1', 'scan2', 'time'}
    assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


def test_lsv(manager):
    kwargs = {
        'current_range_max': get_current_range(30),
        'current_range_min': get_current_range(4),
        'current_range_start': get_current_range(8),
        'begin_potential': -1.0,
        'end_potential': 1.0,
        'step_potential': 0.1,
        'scanrate': 2.0,
    }

    method_old = linear_sweep_voltammetry(**kwargs)
    assert isinstance(method_old, PSLinearSweep)

    method = LinearSweepParameters(**kwargs)
    measurement = manager.measure(method.to_dotnet_method())

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 1

    dataset = measurement.dataset
    assert len(dataset) == 4

    assert dataset.array_names == {'charge', 'potential', 'current', 'time'}
    assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


def test_swv(manager):
    kwargs = {
        'current_range_max': get_current_range(30),
        'current_range_min': get_current_range(4),
        'current_range_start': get_current_range(8),
        'equilibration_time': 0.0,
        'begin_potential': -0.5,
        'end_potential': 0.5,
        'step_potential': 0.1,
        'frequency': 10.0,
        'amplitude': 0.05,
        'record_forward_and_reverse_currents': True,
    }

    method_old = square_wave_voltammetry(**kwargs)
    assert isinstance(method_old, PSSquareWave)

    method = SquareWaveParameters(**kwargs)
    measurement = manager.measure(method.to_dotnet_method())

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 1

    dataset = measurement.dataset
    assert len(dataset) == 5

    assert dataset.array_names == {'potential', 'current', 'time', 'reverse', 'forward'}
    assert dataset.array_quantities == {'Current', 'Potential', 'Time'}


def test_cp(manager):
    kwargs = {
        'potential_range_max': get_potential_range(7),
        'potential_range_min': get_potential_range(1),
        'potential_range_start': get_potential_range(7),
        'current': 0.0,
        'applied_current_range': get_current_range(6),
        'interval_time': 0.1,
        'run_time': 1.0,
    }

    method_old = chronopotentiometry(**kwargs)
    assert isinstance(method_old, PSPotentiometry)

    method = PotentiometryParameters(**kwargs)
    measurement = manager.measure(method.to_dotnet_method())

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 1

    dataset = measurement.dataset
    assert len(dataset) == 4

    assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
    assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


def test_ocp(manager):
    kwargs = {
        'potential_range_max': get_potential_range(7),
        'potential_range_min': get_potential_range(1),
        'potential_range_start': get_potential_range(7),
        'interval_time': 0.1,
        'run_time': 1.0,
    }

    method_old = open_circuit_potentiometry(**kwargs)
    assert isinstance(method_old, PSOpenCircuitPotentiometry)

    method = OpenCircuitPotentiometryParameters(**kwargs)
    measurement = manager.measure(method.to_dotnet_method())

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 1

    dataset = measurement.dataset
    assert len(dataset) == 2

    assert dataset.array_names == {'potential', 'time'}
    assert dataset.array_quantities == {'Potential', 'Time'}
