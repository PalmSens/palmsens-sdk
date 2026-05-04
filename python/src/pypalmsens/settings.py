"""This module contains the public api for classes for method configuration."""

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
from ._types import (
    AllowedCurrentRanges,
    AllowedDeviceState,
    AllowedMethods,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
)

__all__ = [
    'AllowedCurrentRanges',
    'AllowedMethods',
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
    'Material',
    'MeasurementTriggers',
    'Multiplexer',
    'PostMeasurement',
    'PotentialLimits',
    'PotentialRange',
    'Pretreatment',
    'VersusOCP',
]
