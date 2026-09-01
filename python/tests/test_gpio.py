from __future__ import annotations

import logging

import pytest
import pytest_asyncio

import pypalmsens as ps
from pypalmsens._instruments import gpio

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instrument, *_ = ps.discover()
    with ps.connect(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield mgr


@pytest_asyncio.fixture(scope='module')
async def manager_async():
    instrument, *_ = await ps.discover_async()
    async with await ps.connect_async(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield mgr


@pytest.mark.parametrize(
    'pins,expected_mask',
    (
        ([0], 1),
        ([1, 3, 5], 42),
        ([1, 1, 1, 1], 2),
        ([4, 2], 20),
        ([2, 4], 20),
    ),
)
def test_pins_to_bitmask(pins, expected_mask):
    assert gpio.pins_to_bitmask(pins) == expected_mask


@pytest.mark.parametrize(
    'mask,expected_pins',
    (
        (1, [0]),
        (42, [1, 3, 5]),
        (2, [1]),
        (20, [2, 4]),
    ),
)
def test_bitmask_to_pins(mask, expected_pins):
    assert gpio.bitmask_to_pins(mask) == expected_pins


def test_raise_if_not_supported(manager):
    client = manager._comm.ClientConnection

    with pytest.raises(gpio.PinNotSupportedError):
        gpio.raise_if_pins_not_supported(client, pins=[-1], mode='read')

    with pytest.raises(gpio.PinNotSupportedError):
        gpio.raise_if_pins_not_supported(client, pins=[-1], mode='write')

    with pytest.raises(gpio.PinNotSupportedError):
        gpio.raise_if_pins_not_supported(client, pins=[9001], mode='read')

    with pytest.raises(gpio.PinNotSupportedError):
        gpio.raise_if_pins_not_supported(client, pins=[9001], mode='write')

    read_pins = gpio.readable_pins(client)
    write_pins = gpio.readable_pins(client)

    gpio.raise_if_pins_not_supported(client, read_pins, mode='read')
    gpio.raise_if_pins_not_supported(client, write_pins, mode='write')


def test_readable_pins(manager):
    pins = manager.gpio.readable_pins
    assert pins
    assert all(isinstance(val, int) for val in pins)


def test_writable_pins(manager):
    pins = manager.gpio.writable_pins
    assert pins
    assert all(isinstance(val, int) for val in pins)


def test_read(manager):
    pins = manager.gpio.readable_pins

    level = manager.gpio.read(pins[0])
    assert level in ('low', 'high')

    levels = manager.gpio.read_many(pins)
    assert len(levels) == len(pins)

    with pytest.raises(gpio.PinNotSupportedError):
        _ = manager.gpio.read(1234)


def test_write(manager):
    pins = manager.gpio.writable_pins

    manager.gpio.write(pins[0], level='high')
    manager.gpio.write(pins[0], level='low')
    manager.gpio.write_many(pins)
    manager.gpio.toggle_many(pins)

    with pytest.raises(ValueError):
        manager.gpio.write(pins[0], level='fail')
