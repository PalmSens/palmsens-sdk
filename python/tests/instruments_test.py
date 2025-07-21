import logging

import pytest

from pspython import pspyinstruments
from pspython.data.measurement import Measurement
from pspython.methods._shared import get_current_range
from pspython.methods.cyclic_voltammetry import CyclicVoltammetryParameters, cyclic_voltammetry

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


def test_cv_old(manager):
    method = cyclic_voltammetry(
        current_range_max=get_current_range(30),  # 1A range
        current_range_min=get_current_range(4),  # 1µA range
        current_range_start=get_current_range(8),  # 1mA range
        equilibration_time=0,  # seconds
        begin_potential=-1,  # V
        vertex1_potential=-1,  # V
        vertex2_potential=1,  # V
        step_potential=0.25,  # V
        scanrate=5,  # V/s
        n_scans=2,  # number of scans
    )

    measurement = manager.measure(method)

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 2

    dataset = measurement.dataset
    assert len(dataset) == 7
    assert dataset.array_names == {'scan1', 'scan2', 'time'}
    assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


def test_cv_new(manager):
    method = CyclicVoltammetryParameters(
        current_range_max=get_current_range(30),  # 1A range
        current_range_min=get_current_range(4),  # 1µA range
        current_range_start=get_current_range(8),  # 1mA range
        equilibration_time=0,  # seconds
        begin_potential=-1,  # V
        vertex1_potential=-1,  # V
        vertex2_potential=1,  # V
        step_potential=0.25,  # V
        scanrate=5,  # V/s
        n_scans=2,  # number of scans
    )

    measurement = manager.measure(method.to_dotnet_method())

    assert measurement
    assert isinstance(measurement, Measurement)
    assert measurement.method.dotnet_method.nScans == 2

    dataset = measurement.dataset
    assert len(dataset) == 7
    assert dataset.array_names == {'scan1', 'scan2', 'time'}
    assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}
