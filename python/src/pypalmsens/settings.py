"""This module contains the public api for classes for method configuration."""

from __future__ import annotations

from ._methods._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    ELevel,
)
from ._methods.settings import (
    BiPot,
    ChargeLimits,
    CurrentLimits,
    CurrentRange,
    DataProcessing,
    EquilibrationTriggers,
    General,
    IrDropCompensation,
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
    'ChargeLimits',
    'CURRENT_RANGE',
    'CurrentLimits',
    'CurrentRange',
    'DataProcessing',
    'ELevel',
    'EquilibrationTriggers',
    'General',
    'IrDropCompensation',
    'MeasurementTriggers',
    'Multiplexer',
    'PostMeasurement',
    'POTENTIAL_RANGE',
    'PotentialLimits',
    'PotentialRange',
    'Pretreatment',
    'VersusOCP',
]
