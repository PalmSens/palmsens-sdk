from __future__ import annotations

import logging

import pytest
import pytest_asyncio
from test_techniques import CP, CV, EIS, MM, MS

import pypalmsens as ps
from pypalmsens._methods import BaseTechnique
from pypalmsens.data import DataArray, DataSet

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope='module')
async def manager():
    instruments = await ps.discover_async()
    async with await ps.connect_async(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield mgr


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_get_instrument_serial(manager):
    val = await manager.get_instrument_serial()
    assert isinstance(val, str)


@pytest.mark.instrument
def test_status_async(manager):
    status = manager.status()
    assert status.device_state == 'Idle'


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_read_current(manager):
    await manager.set_cell(True)

    await manager.set_current_range('1uA')
    val1 = await manager.read_current()
    assert val1

    await manager.set_current_range('10uA')
    val2 = await manager.read_current()
    assert val2

    await manager.set_cell(False)


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_read_potential(manager):
    await manager.set_cell(True)

    await manager.set_potential(1)
    val1 = await manager.read_potential()
    assert val1

    await manager.set_potential(0)
    val2 = await manager.read_potential()
    assert val2

    await manager.set_cell(False)


@pytest.mark.asyncio
@pytest.mark.instrument
@pytest.mark.parametrize(
    'method',
    (
        CV,
        CP,
        EIS,
        MS,
        MM,
    ),
)
async def test_measure(manager, method):
    params = BaseTechnique._registry[method.id].from_dict(method.kwargs)
    measurement = await manager.measure(params)

    method.validate(measurement)


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_callback(manager):
    points = []

    def callback(data):
        points.append(data)

    params = ps.LinearSweepVoltammetry(scanrate=1)
    _ = await manager.measure(params, callback=callback)

    assert len(points) == 11

    point = points[-1]
    assert point.start == 10

    assert isinstance(point.x_array, DataArray)
    assert point.x_array.name == 'potential'
    assert len(point.x_array) == 11

    assert isinstance(point.y_array, DataArray)
    assert point.y_array.name == 'current'
    assert len(point.y_array) == 11


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_callback_eis(manager):
    points = []

    def callback(data):
        points.append(data)

    params = ps.ElectrochemicalImpedanceSpectroscopy(
        frequency_type='fixed',
        scan_type='fixed',
    )
    _ = await manager.measure(params, callback=callback)

    assert len(points) == 1

    point = points[0]

    assert point.start == 0
    assert isinstance(point.data, DataSet)
    assert point.data.n_points == 1
