"""This module contains the public api for classes for method configuration."""

from __future__ import annotations

from ._methods._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    ELevel,
    ILevel,
)
from ._methods.settings import (
    BiPot,
    ChargeLimits,
    CurrentLimits,
    CurrentRange,
    DataProcessing,
    DelayTriggers,
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
    'DelayTriggers',
    'ELevel',
    'ILevel',
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
