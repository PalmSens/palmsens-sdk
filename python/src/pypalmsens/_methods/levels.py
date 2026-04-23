from __future__ import annotations

from collections.abc import Sequence
from dataclasses import field
from typing import Literal

import PalmSens

from .._helpers import single_to_double
from .base_model import BaseModel


def convert_bools_to_int(lst: Sequence[bool]) -> int:
    """Convert e.g. [True, False, True, False] to 5."""
    return int(''.join('01'[set_high] for set_high in reversed(lst)), base=2)


def convert_int_to_bools(val: int) -> tuple[bool, bool, bool, bool]:
    """Convert e.g. 5 to [True, False, True, False]."""
    lst = tuple([bool(int(_)) for _ in reversed(f'{val:04b}')])
    assert len(lst) == 4  # specify length to make mypy happy
    return lst


class ELevel(BaseModel):
    """Create a multi-step amperometry level method object."""

    level: float = 0.0
    """Level in V."""

    duration: float = 1.0
    """Duration in s."""

    record: bool = True
    """Record the current."""

    limit_current_max: float | None = None
    """Limit current max in µA. Set to None to disable."""

    limit_current_min: float | None = None
    """Limit current min in µA. Set to None to disable."""

    trigger_lines: Sequence[Literal[0, 1, 2, 3]] = field(default_factory=list)
    """Trigger at level lines.

    Set digital output lines at start of measurement, end of equilibration.
    Accepted values: 0 for d0, 1 for d1, 2 for d2, 3 for d3.
    """

    @property
    def use_limits(self) -> bool:
        """Return True if instance sets current limits."""
        use_limit_current_min = self.limit_current_min is not None
        use_limit_current_max = self.limit_current_max is not None

        return use_limit_current_min or use_limit_current_max

    def to_psobj(self) -> PalmSens.Techniques.ELevel:
        obj = PalmSens.Techniques.ELevel()

        obj.Level = self.level
        obj.Duration = self.duration
        obj.Record = self.record

        obj.UseMaxLimit = self.limit_current_max is not None
        obj.MaxLimit = self.limit_current_max or 0.0
        obj.UseMinLimit = self.limit_current_min is not None
        obj.MinLimit = self.limit_current_min or 0.0

        obj.UseTriggerOnStart = bool(self.trigger_lines)

        trigger_bools = [(val in self.trigger_lines) for val in (0, 1, 2, 3)]

        obj.TriggerValueOnStart = convert_bools_to_int(trigger_bools)

        return obj

    @classmethod
    def from_psobj(cls, psobj: PalmSens.Techniques.ELevel):
        """Construct ELevel dataclass from PalmSens.Techniques.ELevel object."""
        trigger_lines: list[Literal[0, 1, 2, 3]] = []

        if psobj.UseTriggerOnStart:
            trigger_bools = convert_int_to_bools(psobj.TriggerValueOnStart)
            for i in (0, 1, 2, 3):
                if trigger_bools[i]:
                    trigger_lines.append(i)

        return cls(
            level=single_to_double(psobj.Level),
            duration=single_to_double(psobj.Duration),
            record=psobj.Record,
            limit_current_max=single_to_double(psobj.MaxLimit) if psobj.MaxLimit else None,
            limit_current_min=single_to_double(psobj.MinLimit) if psobj.MinLimit else None,
            trigger_lines=trigger_lines,
        )


class ILevel(BaseModel):
    """Create a multi-step potentiometry level method object."""

    level: float = 0.0
    """Level in I.

    This value is multiplied by the applied current range."""

    duration: float = 1.0
    """Duration in s."""

    record: bool = True
    """Record the potential."""

    limit_potential_max: float | None = None
    """Limit potential max in V. Set to None to disable."""

    limit_potential_min: float | None = None
    """Limit potential min in V. Set to None to disable."""

    trigger_lines: Sequence[Literal[0, 1, 2, 3]] = field(default_factory=list)
    """Trigger at level lines.

    Set digital output lines at start of measurement, end of equilibration.
    Accepted values: 0 for d0, 1 for d1, 2 for d2, 3 for d3.
    """

    @property
    def use_limits(self) -> bool:
        """Return True if instance sets current limits."""
        use_limit_potential_min = self.limit_potential_min is not None
        use_limit_potential_max = self.limit_potential_max is not None

        return use_limit_potential_min or use_limit_potential_max

    def to_psobj(self) -> PalmSens.Techniques.ELevel:
        obj = PalmSens.Techniques.ELevel()

        obj.Level = self.level
        obj.Duration = self.duration
        obj.Record = self.record

        obj.UseMaxLimit = self.limit_potential_max is not None
        obj.MaxLimit = self.limit_potential_max or 0.0
        obj.UseMinLimit = self.limit_potential_min is not None
        obj.MinLimit = self.limit_potential_min or 0.0

        obj.UseTriggerOnStart = bool(self.trigger_lines)

        trigger_bools = [(val in self.trigger_lines) for val in (0, 1, 2, 3)]

        obj.TriggerValueOnStart = convert_bools_to_int(trigger_bools)

        return obj

    @classmethod
    def from_psobj(cls, psobj: PalmSens.Techniques.ELevel):
        """Construct ILevel dataclass from PalmSens.Techniques.ELevel object."""
        trigger_lines: list[Literal[0, 1, 2, 3]] = []

        if psobj.UseTriggerOnStart:
            trigger_bools = convert_int_to_bools(psobj.TriggerValueOnStart)
            for i in (0, 1, 2, 3):
                if trigger_bools[i]:
                    trigger_lines.append(i)

        return cls(
            level=single_to_double(psobj.Level),
            duration=single_to_double(psobj.Duration),
            record=psobj.Record,
            limit_potential_max=single_to_double(psobj.MaxLimit) if psobj.MaxLimit else None,
            limit_potential_min=single_to_double(psobj.MinLimit) if psobj.MinLimit else None,
            trigger_lines=trigger_lines,
        )
