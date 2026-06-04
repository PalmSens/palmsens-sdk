"""Define classes for energy measurements."""

from __future__ import annotations

from ._methods.energy import BatteryCycling as experimental_BatteryCycling
from ._methods.energy import ConstantPower as experimental_ConstantPower
from ._methods.energy import ConstantResistance as experimental_ConstantResistance

__all__ = [
    'experimental_BatteryCycling',
    'experimental_ConstantPower',
    'experimental_ConstantResistance',
]
