from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from PalmSens import Method as PSMethod

from . import techniques

if TYPE_CHECKING:
    from .techniques import ParameterType


class Method:
    """Wrapper for PalmSens.Method."""

    def __init__(self, *, psmethod: PSMethod):
        self.psmethod = psmethod

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r}, id={self.id!r})'

    @property
    def id(self) -> str:
        """Unique id for method."""
        return self.psmethod.MethodID

    @property
    def name(self) -> str:
        """Name for the technique."""
        return self.psmethod.Name

    @property
    def short_name(self) -> str:
        """Short name for the technique."""
        return self.psmethod.ShortName

    @property
    def technique_number(self) -> int:
        """The technique number used in the firmware."""
        return self.psmethod.Technique

    def to_parameters(self) -> ParameterType:
        """Extract techniques parameters as dataclass."""
        return techniques.psmethod_to_parameters(psmethod=self.psmethod)

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary with technique parameters."""
        return asdict(self.to_parameters())
