from __future__ import annotations

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
