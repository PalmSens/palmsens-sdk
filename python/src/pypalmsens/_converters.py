from __future__ import annotations

import numpy as np
import PalmSens

from ._types import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
)


def single_to_double(val: float) -> float:
    """Cast single precision to double precision.

    Pythonnet returns System.Single, whereas python defaults to double precision.
    This leads to incorrect rounding, which makes comparing values difficult.

    By going through np.float32/str you can correctly round back to python float
    (which is double precision)."""
    return float(str(np.float32(val)))


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
    pr = getattr(PalmSens.PotentialRanges, attr)

    return PalmSens.PotentialRange(pr)


def pr_enum_to_string(enum: PalmSens.PotentialRange) -> AllowedPotentialRanges:
    """Convert PotentialRange enum to literal string."""
    pr = enum.PR
    return pr.ToString().lstrip('pr')
