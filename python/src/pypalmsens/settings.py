"""This module contains the public api for classes for method configuration."""

from __future__ import annotations

from ._methods._shared import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
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
    'AllowedCurrentRanges',
    'AllowedPotentialRanges',
    'BiPot',
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
    'MeasurementTriggers',
    'Multiplexer',
    'PostMeasurement',
    'PotentialLimits',
    'PotentialRange',
    'Pretreatment',
    'VersusOCP',
]
