import typing

class DualEISModes(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Bipot : DualEISModes # 1
    ReferenceVersusSense2 : DualEISModes # 2
    SenseWorkingElectrodeVsSense2 : DualEISModes # 4


class EnumFrequencyMode(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Logarithmic : EnumFrequencyMode # 0
    Linear : EnumFrequencyMode # 1
    Custom : EnumFrequencyMode # 2


class enumFrequencyType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Fixed : enumFrequencyType # 0
    Scan : enumFrequencyType # 1


class enumScanType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    PGScan : enumScanType # 0
    TimeScan : enumScanType # 1
    Fixed : enumScanType # 2
