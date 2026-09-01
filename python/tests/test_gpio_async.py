from __future__ import annotations

import logging

import pytest
import pytest_asyncio

import pypalmsens as ps
from pypalmsens._instruments import gpio

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope='module')
async def manager():
    instrument, *_ = await ps.discover_async()
    async with await ps.connect_async(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield mgr


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_read_async(manager):
    pins = manager.gpio.readable_pins

    level = await manager.gpio.read_async(pins[0])
    assert level in ('low', 'high')

    levels = await manager.gpio.read_many_async(pins)
    assert len(levels) == len(pins)

    with pytest.raises(gpio.PinNotSupportedError):
        _ = await manager.gpio.read_async(1234)


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_write_async(manager):
    pins = manager.gpio.writable_pins

    await manager.gpio.write_async(pins[0], level='high')
    await manager.gpio.write_async(pins[0], level='low')
    await manager.gpio.write_many_async(pins)
    await manager.gpio.toggle_many_async(pins)

    with pytest.raises(ValueError):
        await manager.gpio.write_async(pins[0], level='fail')
