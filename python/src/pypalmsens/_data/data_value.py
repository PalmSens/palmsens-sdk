from __future__ import annotations

from dataclasses import dataclass

import PalmSens
from typing_extensions import override

from .._methods.shared import cr_enum_to_string, pr_enum_to_string
from ..settings import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
)


@dataclass(slots=True)
class PotentialReading:
    """Potential reading data class."""

    potential_range: AllowedPotentialRanges
    """Active potential range (PR) for this data point."""

    potential: float
    """Potential in V."""

    potential_in_range: float
    """Raw potential value expressed in the active potential range.

    `potential` = `potential_in_range` * PR, e.g. 2.0 * 100mV = 0.2V
    """

    timing_status: AllowedTimingStatus
    """Status of the potential timing."""

    reading_status: AllowedReadingStatus
    """Status of the potential reading."""

    @override
    def __str__(self):
        return f'{self.potential:.3f} V'

    @classmethod
    def _from_psobject(cls, obj: PalmSens.Data.VoltageReading):
        return cls(
            potential_range=pr_enum_to_string(obj.Range),
            potential=obj.Value,
            potential_in_range=obj.ValueInRange,
            timing_status=str(obj.ReadingStatus),  # type: ignore
            reading_status=str(obj.TimingStatus),  # type: ignore
        )


@dataclass(slots=True)
class CurrentReading:
    """Current reading data class."""

    current_range: AllowedCurrentRanges
    """Active current range (CR) for this data point."""

    current: float
    """Current in μA."""

    current_in_range: float
    """Raw current value expressed in the active current range.

    `current` = `current_in_range` * CR, e.g. 0.2 * 100uA = 2.0 uA
    """

    timing_status: AllowedTimingStatus
    """Status of the current timing."""

    reading_status: AllowedReadingStatus
    """Status of the current reading."""

    @override
    def __str__(self):
        return f'{self.current_in_range:.3f} * {self.current_range}'

    @classmethod
    def _from_psobject(cls, obj: PalmSens.Data.CurrentReading):
        return cls(
            current_range=cr_enum_to_string(obj.CurrentRange),
            current=obj.Value,
            current_in_range=obj.ValueInRange,
            timing_status=str(obj.ReadingStatus),  # type:ignore
            reading_status=str(obj.TimingStatus),  # type:ignore
        )
