from __future__ import annotations

from typing import Literal

from . import techniques
from .mixins import MaterialMixin


class CorrosionPotential(techniques.BaseOpenCircuitPotentiometry, MaterialMixin):
    """Create corrosion potential method parameters.

    The method is equivalent to Open Circuit Potentiometry."""

    id: Literal['cpot'] = 'cpot'
    """Unique method identifier."""


class CyclicPolarization(techniques.BaseCyclicVoltammetry, MaterialMixin):
    """Create cyclic polarization method parameters.

    The method is equivalent to Cyclic Voltammetry."""

    id: Literal['cp'] = 'cp'
    """Unique method identifier."""


class Galvanostatic(techniques.BaseChronoPotentiometry, MaterialMixin):
    """Create galvanostatic method parameters.

    The method is equivalent to Chronopotentiometry."""

    id: Literal['gs'] = 'gs'
    """Unique method identifier."""


class LinearPolarization(techniques.BaseLinearSweepVoltammetry, MaterialMixin):
    """Create linear polarization method parameters.

    Linear polarization is typically used to study the corrosion response of metallic coatings.
    The method is equivalent to Linear Sweep Voltammetry.
    """

    id: Literal['lp'] = 'lp'
    """Unique method identifier."""


class Potentiostatic(techniques.BaseChronoAmperometry, MaterialMixin):
    """Create potentiostatic method parameters.

    The method is equivalent to Chronoamperometry."""

    id: Literal['ps'] = 'ps'
    """Unique method identifier."""
