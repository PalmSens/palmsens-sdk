from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

from PalmSens import (
    CurrentRange,
    CurrentRanges,
    ExtraValueMask,
    PotentialRange,
    PotentialRanges,
    Techniques,
)

from .._shared import single_to_double


class CURRENT_RANGE(Enum):
    """Get the id for a given current range."""

    cr_100_pA = 0
    cr_1_nA = 1
    cr_10_nA = 2
    cr_100_nA = 3
    cr_1_uA = 4
    cr_10_uA = 5
    cr_100_uA = 6
    cr_1_mA = 7
    cr_10_mA = 8
    cr_100_mA = 9
    cr_2_uA = 10
    cr_4_uA = 11
    cr_8_uA = 12
    cr_16_uA = 13
    cr_32_uA = 14
    cr_63_uA = 26
    cr_125_uA = 17
    cr_250_uA = 18
    cr_500_uA = 19
    cr_5_mA = 20
    cr_6_uA = 21
    cr_13_uA = 22
    cr_25_uA = 23
    cr_50_uA = 24
    cr_200_uA = 25
    cr_1_A = 30

    def _to_psobj(self):
        """Get equivalent PS object."""
        return CurrentRange(CurrentRanges(self.value))

    @classmethod
    def _from_psobj(cls, psobj):
        """Convert from PS object."""
        return cls(int(CurrentRange.GetCRfromCRByte(psobj.CRbyte)))


class POTENTIAL_RANGE(Enum):
    """Get the id for a given current range."""

    pr_1_mV = 0
    pr_10_mV = 1
    pr_20_mV = 2
    pr_50_mV = 3
    pr_100_mV = 4
    pr_200_mV = 5
    pr_500_mV = 6
    pr_1_V = 7

    def _to_psobj(self):
        """Get equivalent PS object."""
        return PotentialRange(PotentialRanges(self.value))

    @classmethod
    def _from_psobj(cls, psobj):
        """Convert from PS object."""
        return cls(int(PotentialRange.get_PR(psobj)))


def convert_bools_to_int(lst: Sequence[bool]) -> int:
    """Convert e.g. [True, False, True, False] to 5."""
    return int(''.join('01'[set_high] for set_high in reversed(lst)), base=2)


def convert_int_to_bools(val) -> tuple[bool, bool, bool, bool]:
    """Convert e.g. 5 to [True, False, True, False]."""
    lst = tuple([bool(int(_)) for _ in reversed(f'{val:04b}')])
    assert len(lst) == 4  # specify length to make mypy happy
    return lst


def set_extra_value_mask(
    obj,
    *,
    enable_bipot_current: bool = False,
    record_auxiliary_input: bool = False,
    record_cell_potential: bool = False,
    record_we_potential: bool = False,
    record_forward_and_reverse_currents: bool = False,
    record_we_current: bool = False,
):
    """Set the extra value mask for a given method."""
    extra_values = 0

    for flag, enum in (
        (enable_bipot_current, ExtraValueMask.BipotWE),
        (record_auxiliary_input, ExtraValueMask.AuxInput),
        (record_cell_potential, ExtraValueMask.CEPotential),
        (record_we_potential, ExtraValueMask.PotentialExtraRE),
        (record_forward_and_reverse_currents, ExtraValueMask.IForwardReverse),
        (record_we_current, ExtraValueMask.CurrentExtraWE),
    ):
        if flag:
            extra_values = extra_values | int(enum)

    obj.ExtraValueMsk = ExtraValueMask(extra_values)


def get_extra_value_mask(obj) -> dict[str, Any]:
    mask = obj.ExtraValueMsk

    ret = {
        'enable_bipot_current': mask.HasFlag(ExtraValueMask.BipotWE),
        'record_auxiliary_input': mask.HasFlag(ExtraValueMask.AuxInput),
        'record_cell_potential': mask.HasFlag(ExtraValueMask.CEPotential),
        'record_we_potential': mask.HasFlag(ExtraValueMask.PotentialExtraRE),
        'record_forward_and_reverse_currents': mask.HasFlag(ExtraValueMask.IForwardReverse),
        'record_we_current': mask.HasFlag(ExtraValueMask.CurrentExtraWE),
    }

    return ret


@dataclass
class ELevel:
    """Create a multi-step amperometry level method object.

    Attributes
    ----------
    level : float
        Level in V (default: 0.0)
    duration : float
        Duration in s (default: 1.0)
    record : bool
        Record the current (default: True)
    use_limit_current_max : bool
        Use limit current max (default: False)
    limit_current_max : float
        Limit current max in µA (default: 0.0)
    use_limit_current_min : bool
        Use limit current min (default: False)
    limit_current_min : float
        Limit current min in µA (default: 0.0)
    trigger_at_level : bool
        Use trigger at level (default: False)
    trigger_at_level_lines : list
        Trigger at level lines (default: [False, False, False, False])
        [d0 high, d1 high, d2 high, d3 high]
    """

    level: float = 0.0
    duration: float = 1.0
    record: bool = True
    use_limit_current_max: bool = False
    limit_current_max: float = 0.0
    use_limit_current_min: bool = False
    limit_current_min: float = 0.0
    trigger_at_level: bool = False
    trigger_at_level_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)

    def to_psobj(self):
        obj = Techniques.ELevel()

        obj.Level = self.level
        obj.Duration = self.duration
        obj.Record = self.record

        obj.UseMaxLimit = self.use_limit_current_max
        obj.MaxLimit = self.limit_current_max
        obj.UseMinLimit = self.use_limit_current_min
        obj.MinLimit = self.limit_current_min

        obj.UseTriggerOnStart = self.trigger_at_level
        obj.TriggerValueOnStart = convert_bools_to_int(self.trigger_at_level_lines)

        return obj

    @classmethod
    def from_psobj(cls, psobj: Techniques.ELevel):
        """Construct ELevel dataclass from PalmSens.Techniques.ELevel object."""
        return cls(
            level=single_to_double(psobj.Level),
            duration=single_to_double(psobj.Duration),
            record=psobj.Record,
            use_limit_current_max=psobj.UseMaxLimit,
            limit_current_max=single_to_double(psobj.MaxLimit),
            use_limit_current_min=psobj.UseMinLimit,
            limit_current_min=single_to_double(psobj.MinLimit),
            trigger_at_level=psobj.UseTriggerOnStart,
            trigger_at_level_lines=convert_int_to_bools(psobj.TriggerValueOnStart),
        )
