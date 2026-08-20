"""Define types and string literals."""

from __future__ import annotations

from ._data.types import AllowedArrayTypes
from ._types import (
    AllowedCurrentRanges,
    AllowedDeviceState,
    AllowedEvents,
    AllowedFrequencyTypes,
    AllowedMethods,
    AllowedMSMethods,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedScanTypes,
    AllowedTimingStatus,
    MethodType,
    MethodTypeCompatible,
    OCPFlag,
)

__all__ = [
    'AllowedArrayTypes',
    'AllowedCurrentRanges',
    'AllowedDeviceState',
    'AllowedEvents',
    'AllowedFrequencyTypes',
    'AllowedMSMethods',
    'AllowedMethods',
    'AllowedPotentialRanges',
    'AllowedReadingStatus',
    'AllowedScanTypes',
    'AllowedTimingStatus',
    'MethodType',
    'MethodTypeCompatible',
    'OCPFlag',
]
