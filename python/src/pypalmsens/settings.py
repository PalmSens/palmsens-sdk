"""This module contains the public api for classes for method configuration."""

from __future__ import annotations

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
    MeasurementTriggers,
    Multiplexer,
    PostMeasurement,
    PotentialLimits,
    PotentialRange,
    Pretreatment,
    VersusOCP,
)
from ._methods.shared import (
    AllowedCurrentRanges,
    AllowedDeviceState,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
    ELevel,
    ILevel,
)

__all__ = [
    'AllowedCurrentRanges',
    'AllowedPotentialRanges',
    'AllowedTimingStatus',
    'AllowedReadingStatus',
    'AllowedDeviceState',
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
    'MeasurementTriggers',
    'Multiplexer',
    'PostMeasurement',
    'PotentialLimits',
    'PotentialRange',
    'Pretreatment',
    'VersusOCP',
]
