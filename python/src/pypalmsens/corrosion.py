"""Define classes for corrosion measurements."""

from __future__ import annotations

from ._methods.corrosion import (
    CorrosionPotential,
    CyclicPolarization,
    Galvanostatic,
    LinearPolarization,
    Potentiostatic,
)
from ._methods.techniques import ElectrochemicalImpedanceSpectroscopy as ImpedanceSpectroscopy

__all__ = [
    'Potentiostatic',
    'CorrosionPotential',
    'CyclicPolarization',
    'LinearPolarization',
    'Galvanostatic',
    'ImpedanceSpectroscopy',  # alias EIS for completeness
]
