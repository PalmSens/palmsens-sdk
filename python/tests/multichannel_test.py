from __future__ import annotations

import pytest
import pytest_asyncio

import pypalmsens as ps
from pypalmsens._data.measurement import Measurement
from pypalmsens._instruments import Instrument


@pytest.fixture
def pool():
    instruments = ps.discover()
    assert len(instruments) >= 0

    with ps.InstrumentPool(instruments) as pool:
        yield pool

    assert pool.is_disconnected() is True


@pytest_asyncio.fixture
async def apool():
    instruments = await ps.discover_async()
    assert len(instruments) >= 0

    async with ps.InstrumentPoolAsync(instruments) as pool:
        yield pool

    assert pool.is_disconnected() is True


@pytest.mark.instrument
def test_pool(pool):
    assert pool.is_connected() is True

    n = len(pool.managers)

    assert pool.managers
    manager = pool.managers[0]

    pool.remove(manager)

    assert manager not in pool.managers

    pool.add(manager)
    assert len(pool.managers) == n
    assert manager in pool.managers


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_pool_async(apool):
    assert apool.is_connected() is True

    n = len(apool.managers)

    assert apool.managers
    manager = apool.managers[0]

    await apool.remove(manager)

    assert manager not in apool.managers

    await apool.add(manager)
    assert len(apool.managers) == n
    assert manager in apool.managers


@pytest.mark.instrument
def test_pool_measure(pool):
    method = ps.LinearSweepVoltammetry(
        end_potential=-0.5,
        begin_potential=0.5,
        step_potential=0.1,
        scanrate=8.0,
    )

    results = pool.measure(method)

    assert len(results) == len(pool.managers)
    assert all(isinstance(item, Measurement) for item in results)


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_pool_measure_async(apool):
    method = ps.LinearSweepVoltammetry(
        end_potential=-0.5,
        begin_potential=0.5,
        step_potential=0.1,
        scanrate=8.0,
    )

    results = await apool.measure(method)

    assert len(results) == len(apool.managers)
    assert all(isinstance(item, Measurement) for item in results)


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_pool_submit_async(apool):
    async def my_func(manager, value):
        assert value == 1
        serial = await manager.get_instrument_serial()
        return serial

    results = await apool.submit(my_func, value=1)

    assert len(results) == len(apool.managers)
    assert all(isinstance(item, str) for item in results)


@pytest.mark.asyncio
@pytest.mark.instrument
@pytest.mark.xfail(raises=ValueError, reason='Requires multichannel device.')
async def test_pool_hw_sync_async(apool):
    method = ps.LinearSweepVoltammetry(
        end_potential=-0.5,
        begin_potential=0.5,
        step_potential=0.1,
        scanrate=8.0,
    )
    method.general.use_hardware_sync = True

    results = await apool.measure(method)

    assert len(results) == len(apool.managers)
    assert all(isinstance(item, Measurement) for item in results)


@pytest.mark.parametrize(
    'devices',
    [
        pytest.param(
            [
                Instrument(id='testCH002', interface='test', device=None),
                Instrument(id='testCH003', interface='test', device=None),
            ],
            id='missing-channel-1',
        ),
        pytest.param(
            [Instrument(id='testCH001', interface='test', device=None)],
            id='not-enough-channels',
        ),
        pytest.param(
            [
                Instrument(id='testCH001', interface='test', device=None),
                Instrument(id='random', interface='test', device=None),
            ],
            id='group-serial-mismatch',
        ),
    ],
)
@pytest.mark.asyncio
@pytest.mark.instrument
async def test_pool_hw_sync_fail(devices):
    method = ps.LinearSweepVoltammetry()
    method.general.use_hardware_sync = True

    pool = ps.InstrumentPoolAsync(devices)
    with pytest.raises(ValueError):
        _ = await pool.measure(method)


@pytest.mark.instrument
def test_pool_instrument():
    device = ps._instruments.Instrument(id='test', interface='test', device=None)
    mgr = ps.InstrumentManagerAsync(device)
    pool = ps.InstrumentPoolAsync([mgr])
    assert pool.managers
