from __future__ import annotations

from collections.abc import Sequence
from dataclasses import field
from typing import Literal

import PalmSens

from .._shared import single_to_double
from .base_model import BaseModel

AllowedCurrentRanges = Literal[
    '100pA',
    '1nA',
    '10nA',
    '100nA',
    '1uA',
    '10uA',
    '100uA',
    '1mA',
    '10mA',
    '100mA',
    '2uA',
    '4uA',
    '8uA',
    '16uA',
    '32uA',
    '63uA',
    '125uA',
    '250uA',
    '500uA',
    '5mA',
    '6uA',
    '13uA',
    '25uA',
    '50uA',
    '200uA',
    '1A',
]

AllowedPotentialRanges = Literal[
    '1mV',
    '10mV',
    '20mV',
    '50mV',
    '100mV',
    '200mV',
    '500mV',
    '1V',
]


def cr_string_to_enum(s: AllowedCurrentRanges) -> PalmSens.CurrentRange:
    """Convert literal string to CurrentRange."""
    attr = f'cr{s}'
    cr = getattr(PalmSens.CurrentRanges, attr)

    return PalmSens.CurrentRange(cr)


def cr_enum_to_string(enum: PalmSens.CurrentRange) -> AllowedCurrentRanges:
    """Convert CurrentRange enum to literal string."""
    cr = enum.Range
    return cr.ToString().lstrip('cr')


def pr_string_to_enum(s: AllowedPotentialRanges) -> PalmSens.PotentialRange:
    """Convert literal string to PotentialRange."""
    attr = f'pr{s}'
    cr = getattr(PalmSens.PotentialRanges, attr)

    return PalmSens.PotentialRange(cr)


def pr_enum_to_string(enum: PalmSens.PotentialRange) -> AllowedPotentialRanges:
    """Convert PotentialRange enum to literal string."""
    pr = enum.PR
    return pr.ToString().lstrip('pr')


def convert_bools_to_int(lst: Sequence[bool]) -> int:
    """Convert e.g. [True, False, True, False] to 5."""
    return int(''.join('01'[set_high] for set_high in reversed(lst)), base=2)


def convert_int_to_bools(val: int) -> tuple[bool, bool, bool, bool]:
    """Convert e.g. 5 to [True, False, True, False]."""
    lst = tuple([bool(int(_)) for _ in reversed(f'{val:04b}')])
    assert len(lst) == 4  # specify length to make mypy happy
    return lst


def set_extra_value_mask(
    obj: PalmSens.Method,
    *,
    enable_bipot_current: bool = False,
    record_auxiliary_input: bool = False,
    record_cell_potential: bool = False,
    record_dc_current: bool = False,
    record_we_potential: bool = False,
    record_forward_and_reverse_currents: bool = False,
    record_we_current: bool = False,
):
    """Set the extra value mask for a given method."""
    extra_values = 0

    for flag, enum in (
        (enable_bipot_current, PalmSens.ExtraValueMask.BipotWE),
        (record_auxiliary_input, PalmSens.ExtraValueMask.AuxInput),
        (record_cell_potential, PalmSens.ExtraValueMask.CEPotential),
        (record_dc_current, PalmSens.ExtraValueMask.DCcurrent),
        (record_we_potential, PalmSens.ExtraValueMask.PotentialExtraRE),
        (record_forward_and_reverse_currents, PalmSens.ExtraValueMask.IForwardReverse),
        (record_we_current, PalmSens.ExtraValueMask.CurrentExtraWE),
    ):
        if flag:
            extra_values = extra_values | int(enum)

    obj.ExtraValueMsk = PalmSens.ExtraValueMask(extra_values)


def get_extra_value_mask(obj: PalmSens.Method) -> dict[str, bool]:
    mask = obj.ExtraValueMsk

    ret = {
        'enable_bipot_current': mask.HasFlag(PalmSens.ExtraValueMask.BipotWE),
        'record_auxiliary_input': mask.HasFlag(PalmSens.ExtraValueMask.AuxInput),
        'record_cell_potential': mask.HasFlag(PalmSens.ExtraValueMask.CEPotential),
        'record_dc_current': mask.HasFlag(PalmSens.ExtraValueMask.DCcurrent),
        'record_we_potential': mask.HasFlag(PalmSens.ExtraValueMask.PotentialExtraRE),
        'record_forward_and_reverse_currents': mask.HasFlag(
            PalmSens.ExtraValueMask.IForwardReverse
        ),
        'record_we_current': mask.HasFlag(PalmSens.ExtraValueMask.CurrentExtraWE),
    }

    return ret


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
    """Record the current."""

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
