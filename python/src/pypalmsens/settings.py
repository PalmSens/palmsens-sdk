"""Define classes for method configuration."""

from __future__ import annotations

import warnings
from typing import Any

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


def __getattr__(name: str) -> Any:
    if name in (
        'AllowedCurrentRanges',
        'AllowedDeviceState',
        'AllowedMethods',
        'AllowedPotentialRanges',
        'AllowedReadingStatus',
        'AllowedTimingStatus',
    ):
        warnings.warn(
            f"{name!r} has moved, use 'pypalmsens.types.{name}'",
            DeprecationWarning,
            stacklevel=2,
        )
        from . import types

        return getattr(types, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


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
