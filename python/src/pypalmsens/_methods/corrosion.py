from __future__ import annotations

from typing import Literal

from . import techniques
from .mixins import MaterialMixin


class CorrosionPotential(techniques.BaseOpenCircuitPotentiometry, MaterialMixin):
    """Create corrosion potential method parameters.

    The method is equivalent to [Open Circuit Potentiometry][pypalmsens.OpenCircuitPotentiometry].

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.CorrosionPotential(
    ...     interval_time=0.1,
    ...     run_time=1.0,
    ...     record_we_current=False,
    ...     record_we_current_range='1uA',
    ... )
    """

    id: Literal['cpot'] = 'cpot'
    """Unique method identifier."""


class CyclicPolarization(techniques.BaseCyclicVoltammetry, MaterialMixin):
    """Create cyclic polarization method parameters.

    The method is equivalent to [Cyclic Voltammetry][pypalmsens.CyclicVoltammetry].

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.CyclicPolarization(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     vertex1_potential=0.5,
    ...     vertex2_potential=-0.5,
    ...     step_potential=0.1,
    ...     scanrate=1.0,
    ...     n_scans=1,
    ... )
    """

    id: Literal['cp'] = 'cp'
    """Unique method identifier."""


class Galvanostatic(techniques.BaseChronoPotentiometry, MaterialMixin):
    """Create galvanostatic method parameters.

    The method is equivalent to [Chronopotentiometry][pypalmsens.ChronoPotentiometry].

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.Galvanostatic(
    ...     current=0.0,
    ...     applied_current_range='100mA',
    ...     interval_time=0.1,
    ...     run_time=1.0,
    ...     record_we_current=False,
    ... )
    """

    id: Literal['gs'] = 'gs'
    """Unique method identifier."""


class LinearPolarization(techniques.BaseLinearSweepVoltammetry, MaterialMixin):
    """Create linear polarization method parameters.

    Linear polarization is typically used to study the corrosion response of metallic coatings.
    The method is equivalent to [Linear Sweep Voltammetry][pypalmsens.LinearSweepVoltammetry].

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.LinearPolarization(
    ...     equilibration_time=0.0,
    ...     begin_potential=-0.5,
    ...     end_potential=0.5,
    ...     step_potential=0.1,
    ...     scanrate=1.0,
    ... )
    """

    id: Literal['lp'] = 'lp'
    """Unique method identifier."""


class Potentiostatic(techniques.BaseChronoAmperometry, MaterialMixin):
    """Create potentiostatic method parameters.

    The method is equivalent to [Chronoamperometry][pypalmsens.ChronoAmperometry].

    Examples
    --------
    >>> import pypalmsens as ps
    >>> method = ps.Potentiostatic(
    ...     equilibration_time=0.0,
    ...     interval_time=0.1,
    ...     potential=0.0,
    ...     run_time=1.0,
    ... )
    """

    id: Literal['ps'] = 'ps'
    """Unique method identifier."""
