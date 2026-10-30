from __future__ import annotations

from collections.abc import Sequence
from dataclasses import field
from typing import Literal

from PalmSens import Techniques as PSTechniques

from .._converters import single_to_double
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
    """A single potential level of a multi-step amperometry method.

    Each level holds the working electrode at a fixed potential for `duration`,
    exactly like a Chronoamperometry step: the current is sampled at the
    method's `interval_time` while the level is active. The levels of a
    [MultiStep Amperometry][pypalmsens.MultiStepAmperometry] method are applied
    one after another, and the entire cycle is repeated `n_cycles` times.

    Switching between levels adds overhead time: on average ~80 ms per step for
    the PalmSens and EmStat 1-3 series, ~1 ms for EmStat4 and EmStat Pico, and
    ~0.4 ms for Nexus.
    """

    level: float = 0.0
    """Potential level in V.

    The potential at which the current is recorded during this level. It must
    be within the applicable potential range of the instrument.
    """

    duration: float = 1.0
    """Duration of the applied potential in s.

    Must be at least 5 times the method's `interval_time` and at most 1,000,000
    s (ca. 278 hours).
    """

    record: bool = True
    """Record the current during this level.

    If `False`, the potential is still applied for `duration`, but the current
    is not recorded.
    """

    limit_current_max: float | None = None
    """Maximum current in µA. Set to None to disable.

    If the current reaches this value, the method proceeds to the next level
    instead of waiting for `duration` to elapse.
    """

    limit_current_min: float | None = None
    """Minimum current in µA. Set to None to disable.

    Same early transition to the next level as `limit_current_max`.
    """

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

    def _to_psobj(self) -> PSTechniques.ELevel:
        obj = PSTechniques.ELevel()

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
    def _from_psobj(cls, psobj: PSTechniques.ELevel):
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
    """A single current level of a multi-step potentiometry method.

    Each level applies a constant current for `duration` while the potential
    response is sampled at the method's `interval_time`. The levels of a
    [MultiStep Potentiometry][pypalmsens.MultiStepPotentiometry] method are
    applied one after another, and the entire cycle is repeated `n_cycles`
    times.

    Switching between levels adds overhead time: on average ~80 ms per step for
    the PalmSens and EmStat 1-3 series, ~1 ms for EmStat4 and EmStat Pico, and
    ~0.4 ms for Nexus.
    """

    level: float = 0.0
    """Current level as a multiple of the applied current range.

    This value is multiplied by the applied current range of the method: with a
    `100uA` range, `level=0.5` applies 50 µA. The largest usable multiplier is
    instrument dependent: ±2 to ±6 times the range for the nA-mA ranges
    (PalmSens2 ±2, PalmSens3 ±3, PalmSens4 ±6, EmStat4 ±3), ±5 below 10 mA and
    ±4.5 for the 10 and 100 mA ranges on Nexus, ±1 for the 1 A range.
    """

    duration: float = 1.0
    """Duration of the applied current in s.

    Must be at least 5 times the method's `interval_time` and at most 1,000,000
    s (ca. 278 hours).
    """

    record: bool = True
    """Record the potential during this level.

    If `False`, the current is still applied for `duration`, but the potential
    is not recorded.
    """

    limit_potential_max: float | None = None
    """Maximum potential in V. Set to None to disable.

    If the potential reaches this value, the method proceeds to the next level
    instead of waiting for `duration` to elapse.
    """

    limit_potential_min: float | None = None
    """Minimum potential in V. Set to None to disable.

    Same early transition to the next level as `limit_potential_max`.
    """

    trigger_lines: Sequence[Literal[0, 1, 2, 3]] = field(default_factory=list)
    """Trigger at level lines.

    Set digital output lines at start of measurement, end of equilibration.
    Accepted values: 0 for d0, 1 for d1, 2 for d2, 3 for d3.
    """

    @property
    def use_limits(self) -> bool:
        """Return True if instance sets potential limits."""
        use_limit_potential_min = self.limit_potential_min is not None
        use_limit_potential_max = self.limit_potential_max is not None

        return use_limit_potential_min or use_limit_potential_max

    def _to_psobj(self) -> PSTechniques.EILevel:
        obj = PSTechniques.EILevel()

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
    def _from_psobj(cls, psobj: PSTechniques.EILevel):
        """Construct ILevel dataclass from PalmSens.Techniques.EILevel object."""
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
