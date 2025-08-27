from __future__ import annotations

from enum import Enum
from typing import Optional


class ArrayType(Enum):
    """Data array type for standard arrays."""

    Unspecified = -1
    """Unspecified"""
    Time = 0
    """Time / s"""
    Potential = 1
    """Potential / V"""
    Current = 2
    """Current / μA"""
    Charge = 3
    """Charge"""
    ExtraValue = 4
    """ExtraValue"""
    Frequency = 5
    """Frequency"""
    Phase = 6
    """Phase"""
    ZRe = 7
    """Z real"""
    ZIm = 8
    """Z imaginary"""
    Iac = 9
    """I AC values"""
    Z = 10
    """Z"""
    Y = 11
    """Y"""
    YRe = 12
    """Y real"""
    YIm = 13
    """Y imaginary"""
    Cs = 14
    """Cs"""
    CsRe = 15
    """Cs real"""
    CsIm = 16
    """Cs imaginary"""
    Index = 17
    """Index"""
    Admittance = 18
    """Admittance"""
    Concentration = 19
    """Concentration"""
    Signal = 20
    """Signal"""
    Func = 21
    """Func"""
    Integral = 22
    """Integral"""
    AuxInput = 23
    """Auxillary input"""
    BipotCurrent = 24
    """Bipot current"""
    BipotPotential = 25
    """Bipot potential"""
    ReverseCurrent = 26
    """Reverse current"""
    CEPotential = 27
    """CE potential"""
    DCCurrent = 28
    """DC current"""
    ForwardCurrent = 29
    """Forward current"""
    PotentialExtraRE = 30
    """Potential setpoint measured back on RE"""
    CurrentExtraWE = 31
    """Current setpoint measured back on WE"""
    InverseDerative_dtdE = 32
    """Inverse derivative dt/dE"""
    mEdc = 33
    """Measured applied DC"""
    Eac = 34
    """E AC values"""
    MeasuredStepStartIndex = 35
    """MeasuredStepStartIndex"""
    miDC = 36
    """Measured I DC values"""
    SE2vsXPotential = 37
    """SE2 vs XPotential"""

    @classmethod
    def _missing_(cls, value):
        return cls.Unspecified


class Status(Enum):
    Unknown = -1
    OK = 0
    Overload = 1
    Underload = 2


def _get_values_from_NETArray(array, start: int = 0, count: Optional[int] = None):
    if not count:
        count = array.Count

    values = []
    for i in range(start, start + count):
        value = array.get_Item(i)
        values.append(float(value.Value))
    return values


def __get_currentranges_from_currentarray(
    arraycurrents, start: int = 0, count: Optional[int] = None
):
    if not count:
        count = arraycurrents.Count
    values = []
    if ArrayType(arraycurrents.ArrayType) == ArrayType.Current:
        for i in range(start, count):
            value = arraycurrents.get_Item(i)
            values.append(str(value.CurrentRange.ToString()))
    return values


def __get_status_from_current_or_potentialarray(
    array, start: int = 0, count: Optional[int] = None
):
    if not count:
        count = array.Count

    values = []
    for i in range(start, count):
        value = array.get_Item(i)
        values.append(str(Status(value.ReadingStatus)))
    return values
