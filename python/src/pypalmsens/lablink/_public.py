from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class LablinkInfo(BaseModel):
    """Basic information about a Lablink hub instance."""

    model_config = ConfigDict(frozen=True, extra='forbid')

    name: str
    """Display name of the hub, e.g. ``"Lablink-42"``."""

    version: str = ''
    """Lablink version string."""

    special_version: str = ''
    """Special variant, empty string if none."""

    os_version: str = ''
    """Operating system running lablink."""

    model: str = ''
    """Hub hardware model designation."""

    serial_number: str = ''
    """Lablink serial number"""

    is_measuring: bool = False
    """Whether a measurement is currently running."""


class InstrumentInfo(BaseModel):
    """Basic information about an Instrument."""

    model_config = ConfigDict(frozen=True, extra='forbid')

    custom_name: str | None
    default_name: str
    is_claimed: bool
    claim_owner: str | None
    is_in_error: bool
    is_measuring: bool
    model: str
    multichannel_id: str
    multichannel_index: int
    in_multichannel_group: bool

    @property
    def name(self) -> str:
        """The name of the instrument."""
        return self.custom_name or self.default_name

    @property
    def status(self) -> Literal['Idle', 'Measuring', 'Error']:
        """The current status of the instrument."""
        if self.is_in_error:
            return 'Error'
        elif self.is_measuring:
            return 'Measuring'
        else:
            return 'Idle'


class MeasurementInfo(BaseModel):
    """Measurement metadata."""
