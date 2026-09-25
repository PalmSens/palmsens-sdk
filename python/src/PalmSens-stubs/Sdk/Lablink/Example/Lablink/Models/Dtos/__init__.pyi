import typing

class DataValueTypes(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Index : DataValueTypes # 0
    CycleIndex : DataValueTypes # 1
    LevelIndex : DataValueTypes # 2
    Timestamp : DataValueTypes # 3
    Frequency : DataValueTypes # 4
    TimingStatus : DataValueTypes # 5
    AppliedCurrent : DataValueTypes # 6
    MeasuredCurrent : DataValueTypes # 7
    ForwardCurrent : DataValueTypes # 8
    ReverseCurrent : DataValueTypes # 9
    ACCurrent : DataValueTypes # 10
    DCCurrent : DataValueTypes # 11
    CurrentRange : DataValueTypes # 12
    CurrentReadingStatus : DataValueTypes # 13
    ForwardCurrentReadingStatus : DataValueTypes # 14
    ReverseCurrentReadingStatus : DataValueTypes # 15
    MeasuredWE2Current : DataValueTypes # 16
    ForwardWE2Current : DataValueTypes # 17
    ReverseWE2Current : DataValueTypes # 18
    ACWE2Current : DataValueTypes # 19
    DCWE2Current : DataValueTypes # 20
    WE2CurrentRange : DataValueTypes # 21
    WE2CurrentReadingStatus : DataValueTypes # 22
    ForwardWE2CurrentReadingStatus : DataValueTypes # 23
    ReverseWE2CurrentReadingStatus : DataValueTypes # 24
    AppliedPotential : DataValueTypes # 25
    AppliedWE2Potential : DataValueTypes # 26
    MeasuredPotential : DataValueTypes # 27
    MeasuredWECEPotential : DataValueTypes # 28
    ACPotential : DataValueTypes # 29
    DCPotential : DataValueTypes # 30
    ACWECEPotential : DataValueTypes # 31
    DCWECEPotential : DataValueTypes # 32
    ACRECEPotential : DataValueTypes # 33
    DCRECEPotential : DataValueTypes # 34
    PotentialRange : DataValueTypes # 35
    PotentialReadingStatus : DataValueTypes # 36
    AuxiliaryPotential : DataValueTypes # 37
    Charge : DataValueTypes # 38
    ImpedanceReal : DataValueTypes # 39
    ImpedanceImaginary : DataValueTypes # 40
    ImpedanceMagnitude : DataValueTypes # 41
    ImpedancePhase : DataValueTypes # 42
    AdmittanceReal : DataValueTypes # 43
    AdmittanceImaginary : DataValueTypes # 44
    AdmittanceMagnitude : DataValueTypes # 45
    CapacitanceReal : DataValueTypes # 46
    CapacitanceImaginary : DataValueTypes # 47
    CapacitanceSeries : DataValueTypes # 48
    ScpValue : DataValueTypes # 49
    dEdt : DataValueTypes # 50
    Temperature : DataValueTypes # 51
    CustomUnit : DataValueTypes # 52


class MeasuringRangeDto:
    @property
    def Exponent(self) -> int: ...
    @Exponent.setter
    def Exponent(self, value: int) -> int: ...
    @property
    def Significant(self) -> int: ...
    @Significant.setter
    def Significant(self, value: int) -> int: ...


class ReadingStatus(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    OK : ReadingStatus # 0
    Overload : ReadingStatus # 1
    Underload : ReadingStatus # 2
    Unknown : ReadingStatus # -1


class TimingStatus(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    OK : TimingStatus # 0
    OverStep : TimingStatus # 1
    Unknown : TimingStatus # -1
