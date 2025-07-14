from enum import Enum
from typing import Optional


class ArrayType(Enum):
    Unspecified = -1
    Time = 0
    Potential = 1
    Current = 2
    Charge = 3
    ExtraValue = 4
    Frequency = 5
    Phase = 6
    ZRe = 7
    ZIm = 8
    Iac = 9
    Z = 10
    Y = 11
    YRe = 12
    YIm = 13
    Cs = 14
    CsRe = 15
    CsIm = 16
    Index = 17
    Admittance = 18
    Concentration = 19
    Signal = 20
    Func = 21
    Integral = 22
    AuxInput = 23
    BipotCurrent = 24
    BipotPotential = 25
    ReverseCurrent = 26
    CEPotential = 27
    DCCurrent = 28
    ForwardCurrent = 29
    PotentialExtraRE = 30
    CurrentExtraWE = 31
    InverseDerative_dtdE = 32
    mEdc = 33
    Eac = 34
    MeasuredStepStartIndex = 35
    miDC = 36

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
