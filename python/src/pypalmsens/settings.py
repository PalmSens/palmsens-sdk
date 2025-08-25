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
    CurrentRanges,
    DataProcessing,
    EquilibrationTriggers,
    General,
    IrDropCompensation,
    MeasurementTriggers,
    Multiplexer,
    PostMeasurement,
    PotentialLimits,
    PotentialRanges,
    Pretreatment,
    VersusOCP,
)

__all__ = [
    'BiPot',
    'ChargeLimits',
    'CURRENT_RANGE',
    'CurrentLimits',
    'CurrentRanges',
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
    'PotentialRanges',
    'Pretreatment',
    'VersusOCP',
]
