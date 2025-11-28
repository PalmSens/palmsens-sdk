from __future__ import annotations

import logging

import pytest
import pytest_asyncio
from test_techniques import CP, CV, EIS, MM, MS

import pypalmsens as ps
from pypalmsens._methods import BaseTechnique

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope='module')
async def manager():
    instruments = ps.discover()
    async with await ps.connect_async(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield mgr


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_get_instrument_serial(manager):
    val = await manager.get_instrument_serial()
    assert isinstance(val, str)


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_read_current(manager):
    await manager.set_cell(True)

    await manager.set_current_range(ps.settings.CURRENT_RANGE.cr_1_uA)
    val1 = await manager.read_current()
    await manager.set_current_range(ps.settings.CURRENT_RANGE.cr_10_uA)
    val2 = await manager.read_current()

    await manager.set_cell(False)

    div = abs(abs(val2 / val1))
    assert 9.0 < div < 11.0


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_read_potential(manager):
    await manager.set_cell(True)
    await manager.set_potential(1)
    val = await manager.read_potential()
    assert 0.95 < abs(val) < 1.05
    await manager.set_potential(0)
    val = await manager.read_potential()
    assert abs(val) < 0.05
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
        points.extend(data)

    params = ps.LinearSweepVoltammetry(scanrate=10)
    _ = await manager.measure(params, callback=callback)

    assert len(points) == 11

    point = points[-1]
    assert isinstance(point, dict)
    assert point['index'] == 11
    assert isinstance(point['x'], float)
    assert point['x_unit'] == 'V'
    assert point['x_type'] == 'Potential'
    assert isinstance(point['y'], float)
    assert point['y_unit'] == 'µA'
    assert point['y_type'] == 'Current'


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_callback_eis(manager):
    points = []

    def callback(data):
        points.extend(data)

    params = ps.ElectrochemicalImpedanceSpectroscopy(
        frequency_type='fixed',
        scan_type='fixed',
        # fixed_frequency=1000,
    )
    _ = await manager.measure(params, callback=callback)

    assert len(points) == 1

    point = points[0]
    assert point['index'] == 1
    assert point['frequency'] == 1000.0
    assert isinstance(point['zre'], float)
    assert isinstance(point['zim'], float)
