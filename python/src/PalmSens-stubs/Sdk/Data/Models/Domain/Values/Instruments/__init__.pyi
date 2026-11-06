import typing

class CellMode(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Unknown : CellMode # 0
    Potentiostatic : CellMode # 1
    Galvanostatic : CellMode # 2


class CellState(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Unknown : CellState # 0
    Off : CellState # 1
    On : CellState # 2


class MainsFrequency(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Undefined : MainsFrequency # 0
    Hz50 : MainsFrequency # 50
    Hz60 : MainsFrequency # 60
    DontCare : MainsFrequency # -1


class MeasurementStage(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Idle : MeasurementStage # 0
    Conditioning : MeasurementStage # 1
    Deposition : MeasurementStage # 2
    VersusOCP : MeasurementStage # 3
    Equilibration : MeasurementStage # 4
    Measurement : MeasurementStage # 5
    DropDetection : MeasurementStage # 6


class MultiChannelRole(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Undefined : MultiChannelRole # 0
    Standalone : MultiChannelRole # 1
    Master : MultiChannelRole # 2
    Slave : MultiChannelRole # 3


class SignalTrain(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Undefined : SignalTrain # 0
    LowSpeed : SignalTrain # 1
    HighSpeed : SignalTrain # 2
    MaximumRange : SignalTrain # 3
