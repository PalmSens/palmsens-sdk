from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

import PalmSens

from .._shared import single_to_double


class CURRENT_RANGE(Enum):
    """Get the id for a given current range.

    Use these when defining a current range."""

    cr_100_pA = 0
    """100 pA"""
    cr_1_nA = 1
    """1 nA"""
    cr_10_nA = 2
    """10 nA"""
    cr_100_nA = 3
    """100 nA"""
    cr_1_uA = 4
    """1 μA"""
    cr_10_uA = 5
    """10 μA"""
    cr_100_uA = 6
    """100 μA"""
    cr_1_mA = 7
    """1 mA"""
    cr_10_mA = 8
    """10 mA"""
    cr_100_mA = 9
    """100 mA"""
    cr_2_uA = 10
    """2 μA"""
    cr_4_uA = 11
    """4 μA"""
    cr_8_uA = 12
    """8 μA"""
    cr_16_uA = 13
    """16 μA"""
    cr_32_uA = 14
    """32 μA"""
    cr_63_uA = 26
    """63 μA"""
    cr_125_uA = 17
    """125 μA"""
    cr_250_uA = 18
    """250 μA"""
    cr_500_uA = 19
    """500 μA"""
    cr_5_mA = 20
    """5 mA"""
    cr_6_uA = 21
    """6 μA"""
    cr_13_uA = 22
    """13 μA"""
    cr_25_uA = 23
    """25 μA"""
    cr_50_uA = 24
    """50 μA"""
    cr_200_uA = 25
    """200 μA"""
    cr_1_A = 30
    """1 A"""

    def _to_psobj(self):
        """Get equivalent PS object."""
        return PalmSens.CurrentRange(PalmSens.CurrentRanges(self.value))

    @classmethod
    def _from_psobj(cls, psobj):
        """Convert from PS object."""
        return cls(int(PalmSens.CurrentRange.GetCRfromCRByte(psobj.CRbyte)))


class POTENTIAL_RANGE(Enum):
    """Get the id for a given current range.

    Use these when defining a potential range."""

    pr_1_mV = 0
    """1 mV"""
    pr_10_mV = 1
    """10 mV"""
    pr_20_mV = 2
    """20 mV"""
    pr_50_mV = 3
    """50 mV"""
    pr_100_mV = 4
    """100 mV"""
    pr_200_mV = 5
    """200 mV"""
    pr_500_mV = 6
    """500 mV"""
    pr_1_V = 7
    """1 V"""

    def _to_psobj(self):
        """Get equivalent PS object."""
        return PalmSens.PotentialRange(PalmSens.PotentialRanges(self.value))

    @classmethod
    def _from_psobj(cls, psobj):
        """Convert from PS object."""
        return cls(int(PalmSens.PotentialRange.get_PR(psobj)))


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
        (enable_bipot_current, PalmSens.ExtraValueMask.BipotWE),
        (record_auxiliary_input, PalmSens.ExtraValueMask.AuxInput),
        (record_cell_potential, PalmSens.ExtraValueMask.CEPotential),
        (record_we_potential, PalmSens.ExtraValueMask.PotentialExtraRE),
        (record_forward_and_reverse_currents, PalmSens.ExtraValueMask.IForwardReverse),
        (record_we_current, PalmSens.ExtraValueMask.CurrentExtraWE),
    ):
        if flag:
            extra_values = extra_values | int(enum)

    obj.ExtraValueMsk = PalmSens.ExtraValueMask(extra_values)


def get_extra_value_mask(obj) -> dict[str, Any]:
    mask = obj.ExtraValueMsk

    ret = {
        'enable_bipot_current': mask.HasFlag(PalmSens.ExtraValueMask.BipotWE),
        'record_auxiliary_input': mask.HasFlag(PalmSens.ExtraValueMask.AuxInput),
        'record_cell_potential': mask.HasFlag(PalmSens.ExtraValueMask.CEPotential),
        'record_we_potential': mask.HasFlag(PalmSens.ExtraValueMask.PotentialExtraRE),
        'record_forward_and_reverse_currents': mask.HasFlag(
            PalmSens.ExtraValueMask.IForwardReverse
        ),
        'record_we_current': mask.HasFlag(PalmSens.ExtraValueMask.CurrentExtraWE),
    }

    return ret


@dataclass
class ELevel:
    """Create a multi-step amperometry level method object."""

    level: float = 0.0
    """Level in V."""

    duration: float = 1.0
    """Duration in s."""

    record: bool = True
    """Record the current."""

    use_limit_current_max: bool = False
    """Use limit current max."""

    limit_current_max: float = 0.0
    """Limit current max in µA."""

    use_limit_current_min: bool = False
    """Use limit current min."""

    limit_current_min: float = 0.0
    """Limit current min in µA."""

    trigger_at_level: bool = False
    """Use trigger at level."""

    trigger_at_level_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)
    """Trigger at level lines.

    Line order : [d0 high, d1 high, d2 high, d3 high]"""

    def to_psobj(self):
        obj = PalmSens.Techniques.ELevel()

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
    def from_psobj(cls, psobj: PalmSens.Techniques.ELevel):
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
