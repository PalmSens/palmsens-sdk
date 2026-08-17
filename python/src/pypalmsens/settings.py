"""Define classes for method configuration."""

from __future__ import annotations

from ._methods.levels import (
    ELevel,
    ILevel,
)
from ._methods.settings import (
    BiPot,
    BiPotCurrentRange,
    ChargeLimits,
    CurrentLimits,
    CurrentRange,
    DataProcessing,
    DelayTriggers,
    EquilibrationTriggers,
    General,
    IrDropCompensation,
    Material,
    MeasurementTriggers,
    Multiplexer,
    PostMeasurement,
    PotentialLimits,
    PotentialRange,
    Pretreatment,
    VersusOCP,
)

__all__ = [
    'BiPot',
    'BiPotCurrentRange',
    'ChargeLimits',
    'CurrentLimits',
    'CurrentRange',
    'DataProcessing',
    'DelayTriggers',
    'ELevel',
    'EquilibrationTriggers',
    'General',
    'ILevel',
    'IrDropCompensation',
    'Material',
    'MeasurementTriggers',
    'Multiplexer',
    'PostMeasurement',
    'PotentialLimits',
    'PotentialRange',
    'Pretreatment',
    'VersusOCP',
]
