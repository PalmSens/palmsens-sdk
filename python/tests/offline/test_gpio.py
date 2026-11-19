from __future__ import annotations

import logging

import pytest

from pypalmsens._instruments import gpio

logger = logging.getLogger(__name__)


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
