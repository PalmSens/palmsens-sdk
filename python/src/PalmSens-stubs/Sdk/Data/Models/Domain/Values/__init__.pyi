import typing, clr, abc
from System import IEquatable_1, IComparable_1, DateTime, Decimal, TimeSpan
from PalmSens.Sdk.Data.Models.Domain import DataValueType
from PalmSens.Sdk.Data.Models.Entities import AxisDataType

class AxisDataTypeVariant(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Time : AxisDataTypeVariant # 0
    Frequency : AxisDataTypeVariant # 1
    Potential : AxisDataTypeVariant # 2
    Current : AxisDataTypeVariant # 3
    Charge : AxisDataTypeVariant # 4
    ImpedanceReal : AxisDataTypeVariant # 5
    ImpedanceImaginary : AxisDataTypeVariant # 6
    ImpedanceMagnitude : AxisDataTypeVariant # 7
    ImpedancePhase : AxisDataTypeVariant # 8
    AdmittanceReal : AxisDataTypeVariant # 9
    AdmittanceImaginary : AxisDataTypeVariant # 10
    AdmittanceMagnitude : AxisDataTypeVariant # 11
    CapacitanceReal : AxisDataTypeVariant # 12
    CapacitanceImaginary : AxisDataTypeVariant # 13
    CapacitanceSeries : AxisDataTypeVariant # 14
    ScpValue : AxisDataTypeVariant # 15
    Temperature : AxisDataTypeVariant # 16
    CycleNumber : AxisDataTypeVariant # 17
    Efficiency : AxisDataTypeVariant # 18
    Capacity : AxisDataTypeVariant # 19
    CustomUnit : AxisDataTypeVariant # 20


class Color(IEquatable_1[Color]):
    # Constructor .ctor(red : Double, green : Double, blue : Double) was skipped since it collides with above method
    # Constructor .ctor(red : Double, green : Double, blue : Double, alpha : Double) was skipped since it collides with above method
    @typing.overload
    def __init__(self, argb: str) -> None: ...
    @typing.overload
    def __init__(self, argb: int) -> None: ...
    @typing.overload
    def __init__(self, red: int, green: int, blue: int) -> None: ...
    @typing.overload
    def __init__(self, red: int, green: int, blue: int, alpha: int) -> None: ...
    AliceBlue : Color
    AntiqueWhite : Color
    Aqua : Color
    Aquamarine : Color
    Azure : Color
    Beige : Color
    Bisque : Color
    Black : Color
    BlanchedAlmond : Color
    Blue : Color
    BlueViolet : Color
    Brown : Color
    BurlyWood : Color
    CadetBlue : Color
    Chartreuse : Color
    Chocolate : Color
    Coral : Color
    CornflowerBlue : Color
    Cornsilk : Color
    Crimson : Color
    Cyan : Color
    DarkBlue : Color
    DarkCyan : Color
    DarkGoldenRod : Color
    DarkGray : Color
    DarkGreen : Color
    DarkGrey : Color
    DarkKhaki : Color
    DarkMagenta : Color
    DarkOliveGreen : Color
    DarkOrange : Color
    DarkOrchid : Color
    DarkRed : Color
    DarkSalmon : Color
    DarkSeaGreen : Color
    DarkSlateBlue : Color
    DarkSlateGray : Color
    DarkSlateGrey : Color
    DarkTurquoise : Color
    DarkViolet : Color
    DeepPink : Color
    DeepSkyBlue : Color
    DimGray : Color
    DimGrey : Color
    DodgerBlue : Color
    FireBrick : Color
    FloralWhite : Color
    ForestGreen : Color
    Fuchsia : Color
    Gainsboro : Color
    GhostWhite : Color
    Gold : Color
    GoldenRod : Color
    Gray : Color
    Green : Color
    GreenYellow : Color
    Grey : Color
    HoneyDew : Color
    HotPink : Color
    IndianRed : Color
    Indigo : Color
    Ivory : Color
    Khaki : Color
    Lavender : Color
    LavenderBlush : Color
    LawnGreen : Color
    LemonChiffon : Color
    LightBlue : Color
    LightCoral : Color
    LightCyan : Color
    LightGoldenRodYellow : Color
    LightGray : Color
    LightGreen : Color
    LightGrey : Color
    LightPink : Color
    LightSalmon : Color
    LightSeaGreen : Color
    LightSkyBlue : Color
    LightSlateGray : Color
    LightSlateGrey : Color
    LightSteelBlue : Color
    LightYellow : Color
    Lime : Color
    LimeGreen : Color
    Linen : Color
    Magenta : Color
    Maroon : Color
    MediumAquamarine : Color
    MediumBlue : Color
    MediumOrchid : Color
    MediumPurple : Color
    MediumSeaGreen : Color
    MediumSlateBlue : Color
    MediumSpringGreen : Color
    MediumTurquoise : Color
    MediumVioletRed : Color
    MidnightBlue : Color
    MintCream : Color
    MistyRose : Color
    Moccasin : Color
    NavajoWhite : Color
    Navy : Color
    NoColor : Color
    OldLace : Color
    Olive : Color
    OliveDrab : Color
    Orange : Color
    OrangeRed : Color
    Orchid : Color
    PaleGoldenRod : Color
    PaleGreen : Color
    PaleTurquoise : Color
    PaleVioletRed : Color
    PapayaWhip : Color
    PeachPuff : Color
    Peru : Color
    Pink : Color
    Plum : Color
    PowderBlue : Color
    Purple : Color
    RebeccaPurple : Color
    Red : Color
    RosyBrown : Color
    RoyalBlue : Color
    SaddleBrown : Color
    Salmon : Color
    SandyBrown : Color
    SeaGreen : Color
    SeaShell : Color
    Sienna : Color
    Silver : Color
    SkyBlue : Color
    SlateBlue : Color
    SlateGray : Color
    SlateGrey : Color
    Snow : Color
    SpringGreen : Color
    SteelBlue : Color
    Tan : Color
    Teal : Color
    Thistle : Color
    Tomato : Color
    Turquoise : Color
    Violet : Color
    Wheat : Color
    White : Color
    WhiteSmoke : Color
    Yellow : Color
    YellowGreen : Color
    @property
    def A(self) -> int: ...
    @A.setter
    def A(self, value: int) -> int: ...
    @property
    def ARGB(self) -> int: ...
    @ARGB.setter
    def ARGB(self, value: int) -> int: ...
    @property
    def B(self) -> int: ...
    @B.setter
    def B(self, value: int) -> int: ...
    @property
    def G(self) -> int: ...
    @G.setter
    def G(self, value: int) -> int: ...
    @property
    def R(self) -> int: ...
    @R.setter
    def R(self, value: int) -> int: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, lhs: Color, rhs: Color) -> bool: ...
    def __ne__(self, lhs: Color, rhs: Color) -> bool: ...
    def ToRgbString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: Color) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class CurrentIcr(IEquatable_1[CurrentIcr], IComparable_1[CurrentIcr]):
    def __init__(self, value: float) -> None: ...
    @property
    def Value(self) -> float: ...
    @classmethod
    @property
    def Zero(cls) -> CurrentIcr: ...
    def CompareTo(self, other: CurrentIcr) -> int: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: CurrentIcr, right: CurrentIcr) -> bool: ...
    # Operator not supported op_Implicit(value: Double)
    # Operator not supported op_Implicit(value: CurrentIcr)
    def __ne__(self, left: CurrentIcr, right: CurrentIcr) -> bool: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: CurrentIcr) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...

    # Skipped ToAmperes due to it being static, abstract and generic.

    ToAmperes : ToAmperes_MethodGroup
    class ToAmperes_MethodGroup:
        @typing.overload
        def __call__(self, currentRange: CurrentRange) -> float:...
        @typing.overload
        def __call__(self, measuringRange: MeasuringRange) -> float:...

    # Skipped ToMicroAmpere due to it being static, abstract and generic.

    ToMicroAmpere : ToMicroAmpere_MethodGroup
    class ToMicroAmpere_MethodGroup:
        @typing.overload
        def __call__(self, currentRange: CurrentRange) -> MicroAmpere:...
        @typing.overload
        def __call__(self, measuringRange: MeasuringRange) -> MicroAmpere:...



class CurrentRange(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    cr100pA : CurrentRange # 0
    cr1nA : CurrentRange # 1
    cr10nA : CurrentRange # 2
    cr100nA : CurrentRange # 3
    cr1uA : CurrentRange # 4
    cr10uA : CurrentRange # 5
    cr100uA : CurrentRange # 6
    cr1mA : CurrentRange # 7
    cr10mA : CurrentRange # 8
    cr100mA : CurrentRange # 9
    cr2uA : CurrentRange # 10
    cr4uA : CurrentRange # 11
    cr8uA : CurrentRange # 12
    cr16uA : CurrentRange # 13
    cr32uA : CurrentRange # 14
    cr125uA : CurrentRange # 17
    cr250uA : CurrentRange # 18
    cr500uA : CurrentRange # 19
    cr5mA : CurrentRange # 20
    cr6uA : CurrentRange # 21
    cr13uA : CurrentRange # 22
    cr25uA : CurrentRange # 23
    cr50uA : CurrentRange # 24
    cr200uA : CurrentRange # 25
    cr63uA : CurrentRange # 26
    cr1mA_shunt : CurrentRange # 27
    cr10mA_shunt : CurrentRange # 28
    cr100mA_shunt : CurrentRange # 29
    cr1A : CurrentRange # 30
    cr2500uA : CurrentRange # 31


class CurveAxesTypes(IEquatable_1[CurveAxesTypes]):
    def __init__(self, XAxisDataValueType: DataValueType, YAxisDataValueType: DataValueType) -> None: ...
    @property
    def XAxisDataType(self) -> AxisDataType: ...
    @property
    def XAxisDataValueType(self) -> DataValueType: ...
    @XAxisDataValueType.setter
    def XAxisDataValueType(self, value: DataValueType) -> DataValueType: ...
    @property
    def YAxisDataType(self) -> AxisDataType: ...
    @property
    def YAxisDataValueType(self) -> DataValueType: ...
    @YAxisDataValueType.setter
    def YAxisDataValueType(self, value: DataValueType) -> DataValueType: ...
    def Deconstruct(self, XAxisDataValueType: clr.Reference[DataValueType], YAxisDataValueType: clr.Reference[DataValueType]) -> None: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: CurveAxesTypes, right: CurveAxesTypes) -> bool: ...
    def __ne__(self, left: CurveAxesTypes, right: CurveAxesTypes) -> bool: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: CurveAxesTypes) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class CurveSymbol(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Square : CurveSymbol # 0
    Diamond : CurveSymbol # 1
    Triangle : CurveSymbol # 2
    Circle : CurveSymbol # 3
    None_ : CurveSymbol # 4


class DataArrayStatusCountType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Oversteps : DataArrayStatusCountType # 0
    Overloads : DataArrayStatusCountType # 1
    Underloads : DataArrayStatusCountType # 2
    NaN : DataArrayStatusCountType # 3


class DataValueTypeVariant(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Index : DataValueTypeVariant # 0
    CycleIndex : DataValueTypeVariant # 1
    LevelIndex : DataValueTypeVariant # 2
    StageIndex : DataValueTypeVariant # 3
    ScanIndex : DataValueTypeVariant # 4
    Timestamp : DataValueTypeVariant # 5
    Frequency : DataValueTypeVariant # 6
    TimingStatus : DataValueTypeVariant # 7
    AppliedCurrent : DataValueTypeVariant # 8
    MeasuredCurrent : DataValueTypeVariant # 9
    ForwardCurrent : DataValueTypeVariant # 10
    ReverseCurrent : DataValueTypeVariant # 11
    ACCurrent : DataValueTypeVariant # 12
    CurrentRange : DataValueTypeVariant # 13
    CurrentReadingStatus : DataValueTypeVariant # 14
    ForwardCurrentReadingStatus : DataValueTypeVariant # 15
    ReverseCurrentReadingStatus : DataValueTypeVariant # 16
    MeasuredWE2Current : DataValueTypeVariant # 17
    ForwardWE2Current : DataValueTypeVariant # 18
    ReverseWE2Current : DataValueTypeVariant # 19
    ACWE2Current : DataValueTypeVariant # 20
    DCWE2Current : DataValueTypeVariant # 21
    WE2CurrentRange : DataValueTypeVariant # 22
    WE2CurrentReadingStatus : DataValueTypeVariant # 23
    ForwardWE2CurrentReadingStatus : DataValueTypeVariant # 24
    ReverseWE2CurrentReadingStatus : DataValueTypeVariant # 25
    AppliedPotential : DataValueTypeVariant # 26
    AppliedWE2Potential : DataValueTypeVariant # 27
    MeasuredPotential : DataValueTypeVariant # 28
    MeasuredWECEPotential : DataValueTypeVariant # 29
    ACPotential : DataValueTypeVariant # 30
    ACWECEPotential : DataValueTypeVariant # 31
    DCWECEPotential : DataValueTypeVariant # 32
    ACRECEPotential : DataValueTypeVariant # 33
    DCRECEPotential : DataValueTypeVariant # 34
    PotentialRange : DataValueTypeVariant # 35
    PotentialReadingStatus : DataValueTypeVariant # 36
    AuxiliaryPotential : DataValueTypeVariant # 37
    Charge : DataValueTypeVariant # 38
    ChargeCapacity : DataValueTypeVariant # 39
    DischargeCapacity : DataValueTypeVariant # 40
    AccumulatedCharge : DataValueTypeVariant # 41
    ImpedanceReal : DataValueTypeVariant # 42
    ImpedanceImaginary : DataValueTypeVariant # 43
    ImpedanceMagnitude : DataValueTypeVariant # 44
    ImpedancePhase : DataValueTypeVariant # 45
    AdmittanceReal : DataValueTypeVariant # 46
    AdmittanceImaginary : DataValueTypeVariant # 47
    AdmittanceMagnitude : DataValueTypeVariant # 48
    CapacitanceReal : DataValueTypeVariant # 49
    CapacitanceImaginary : DataValueTypeVariant # 50
    CapacitanceSeries : DataValueTypeVariant # 51
    ScpValue : DataValueTypeVariant # 52
    dEdt : DataValueTypeVariant # 53
    Temperature : DataValueTypeVariant # 54
    CustomUnit : DataValueTypeVariant # 55
    CoulombicEfficiency : DataValueTypeVariant # 56
    EnergyEfficiency : DataValueTypeVariant # 57
    VoltageEfficiency : DataValueTypeVariant # 58


class DataVisualizationConvention(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    IUPAC : DataVisualizationConvention # 0
    Polarographic : DataVisualizationConvention # 1


class EISPlotMode(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    ZZvsX : EISPlotMode # 0
    LogZPhasevsLogF : EISPlotMode # 1
    ZPhasevsX : EISPlotMode # 2
    RctvsX : EISPlotMode # 3
    ZvsZ : EISPlotMode # 4
    LogZvsLogF : EISPlotMode # 5
    YvsY : EISPlotMode # 6
    YYvsLogF : EISPlotMode # 7
    LogYvsLogF : EISPlotMode # 8
    YYvsX : EISPlotMode # 9
    YvsX : EISPlotMode # 10
    CvsC : EISPlotMode # 11
    CvsX : EISPlotMode # 12
    None_ : EISPlotMode # -1


class EndpointConnectionType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Unknown : EndpointConnectionType # 0
    Usb : EndpointConnectionType # 1
    Bluetooth : EndpointConnectionType # 2
    InternetProtocol : EndpointConnectionType # 3
    Lablink : EndpointConnectionType # 4


class FirmwareReleaseType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Unknown : FirmwareReleaseType # 0
    Debug : FirmwareReleaseType # 1
    Beta : FirmwareReleaseType # 2
    Release : FirmwareReleaseType # 3


class FirmwareVersion(IEquatable_1[FirmwareVersion], IComparable_1[FirmwareVersion]):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, major: int, minor: int) -> None: ...
    @typing.overload
    def __init__(self, major: int, minor: int, patch: int) -> None: ...
    @typing.overload
    def __init__(self, Major: int, Minor: int, Patch: int, ReleaseType: FirmwareReleaseType, ReleaseDate: DateTime) -> None: ...
    @property
    def Major(self) -> int: ...
    @Major.setter
    def Major(self, value: int) -> int: ...
    @property
    def Minor(self) -> int: ...
    @Minor.setter
    def Minor(self, value: int) -> int: ...
    @property
    def Patch(self) -> int: ...
    @Patch.setter
    def Patch(self, value: int) -> int: ...
    @property
    def ReleaseDate(self) -> DateTime: ...
    @ReleaseDate.setter
    def ReleaseDate(self, value: DateTime) -> DateTime: ...
    @property
    def ReleaseType(self) -> FirmwareReleaseType: ...
    @ReleaseType.setter
    def ReleaseType(self, value: FirmwareReleaseType) -> FirmwareReleaseType: ...
    def CompareTo(self, other: FirmwareVersion) -> int: ...
    def Deconstruct(self, Major: clr.Reference[int], Minor: clr.Reference[int], Patch: clr.Reference[int], ReleaseType: clr.Reference[FirmwareReleaseType], ReleaseDate: clr.Reference[DateTime]) -> None: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: FirmwareVersion, right: FirmwareVersion) -> bool: ...
    def __gt__(self, lhs: FirmwareVersion, rhs: FirmwareVersion) -> bool: ...
    def __ge__(self, lhs: FirmwareVersion, rhs: FirmwareVersion) -> bool: ...
    def __ne__(self, left: FirmwareVersion, right: FirmwareVersion) -> bool: ...
    def __lt__(self, lhs: FirmwareVersion, rhs: FirmwareVersion) -> bool: ...
    def __le__(self, lhs: FirmwareVersion, rhs: FirmwareVersion) -> bool: ...
    @staticmethod
    def Parse(str: str) -> FirmwareVersion: ...
    def ToSimpleString(self) -> str: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: FirmwareVersion) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class HardwareVersion(IEquatable_1[HardwareVersion], IComparable_1[HardwareVersion]):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, Major: int, Minor: int) -> None: ...
    @property
    def Major(self) -> int: ...
    @Major.setter
    def Major(self, value: int) -> int: ...
    @property
    def Minor(self) -> int: ...
    @Minor.setter
    def Minor(self, value: int) -> int: ...
    def CompareTo(self, other: HardwareVersion) -> int: ...
    def Deconstruct(self, Major: clr.Reference[int], Minor: clr.Reference[int]) -> None: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: HardwareVersion, right: HardwareVersion) -> bool: ...
    def __ne__(self, left: HardwareVersion, right: HardwareVersion) -> bool: ...
    @staticmethod
    def Parse(str: str) -> HardwareVersion: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: HardwareVersion) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class HSVColor:
    @typing.overload
    def __init__(self, hue: float, saturation: float, value: float) -> None: ...
    @typing.overload
    def __init__(self, hue: float, saturation: float, value: float, alpha: float) -> None: ...
    @property
    def A(self) -> float: ...
    @A.setter
    def A(self, value: float) -> float: ...
    @property
    def H(self) -> float: ...
    @H.setter
    def H(self, value: float) -> float: ...
    @property
    def S(self) -> float: ...
    @S.setter
    def S(self, value: float) -> float: ...
    @property
    def V(self) -> float: ...
    @V.setter
    def V(self, value: float) -> float: ...
    @staticmethod
    def Blend(color1: HSVColor, color2: HSVColor, ratio: float) -> HSVColor: ...
    def Darken(self, amount: float) -> None: ...
    def Lighten(self, amount: float) -> None: ...
    # Operator not supported op_Implicit(color: Color)
    # Operator not supported op_Implicit(hsvColor: HSVColor)


class InstrumentFamily(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    PalmSens4 : InstrumentFamily # 0
    EmStat4 : InstrumentFamily # 1
    Nexus : InstrumentFamily # 2
    Hex1EmStat : InstrumentFamily # 3
    Pico : InstrumentFamily # 4


class InstrumentModel(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Uninitialised : InstrumentModel # 0
    PalmSens1 : InstrumentModel # 1
    PalmSens2 : InstrumentModel # 2
    PalmSens3 : InstrumentModel # 3
    EmStat1 : InstrumentModel # 4
    EmStat2 : InstrumentModel # 5
    EmStat3 : InstrumentModel # 6
    EmStat3Plus : InstrumentModel # 7
    EmStat3BiPot : InstrumentModel # 8
    PalmSens4 : InstrumentModel # 9
    EmStatPico : InstrumentModel # 10
    EmStat4HR : InstrumentModel # 11
    EmStat4LR : InstrumentModel # 12
    Nexus : InstrumentModel # 13
    EmStatPicoXR : InstrumentModel # 14
    Unknown : InstrumentModel # 2147483647


class InstrumentModelExtensions(abc.ABC):
    @staticmethod
    def ToFamily(model: InstrumentModel) -> InstrumentFamily: ...
    @staticmethod
    def ToProtocol(model: InstrumentModel) -> InstrumentProtocol: ...


class InstrumentProtocol(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    None_ : InstrumentProtocol # 0
    Hex0 : InstrumentProtocol # 1
    Hex1 : InstrumentProtocol # 2
    MethodScript : InstrumentProtocol # 4
    All : InstrumentProtocol # 255


class InstrumentSerial(IEquatable_1[InstrumentSerial]):
    def __init__(self, Serial: str) -> None: ...
    @property
    def Serial(self) -> str: ...
    @Serial.setter
    def Serial(self, value: str) -> str: ...
    def Deconstruct(self, Serial: clr.Reference[str]) -> None: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: InstrumentSerial, right: InstrumentSerial) -> bool: ...
    # Operator not supported op_Implicit(serial: InstrumentSerial)
    def __ne__(self, left: InstrumentSerial, right: InstrumentSerial) -> bool: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: InstrumentSerial) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class LablinkSerial(IEquatable_1[LablinkSerial]):
    def __init__(self, Serial: str) -> None: ...
    @property
    def Serial(self) -> str: ...
    @Serial.setter
    def Serial(self, value: str) -> str: ...
    def Deconstruct(self, Serial: clr.Reference[str]) -> None: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: LablinkSerial, right: LablinkSerial) -> bool: ...
    # Operator not supported op_Implicit(serial: LablinkSerial)
    def __ne__(self, left: LablinkSerial, right: LablinkSerial) -> bool: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: LablinkSerial) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class MeasuredOrApplied(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Measured : MeasuredOrApplied # 0
    Applied : MeasuredOrApplied # 1


class MeasuringRange(IComparable_1[MeasuringRange], IEquatable_1[MeasuringRange]):
    @typing.overload
    def __init__(self, range: Decimal) -> None: ...
    @typing.overload
    def __init__(self, significant: int, exponent: int) -> None: ...
    One : MeasuringRange
    @property
    def Exponent(self) -> int: ...
    @Exponent.setter
    def Exponent(self, value: int) -> int: ...
    @property
    def Prefix(self) -> str: ...
    @property
    def Significant(self) -> int: ...
    @Significant.setter
    def Significant(self, value: int) -> int: ...
    @property
    def Value(self) -> int: ...
    def CompareTo(self, other: MeasuringRange) -> int: ...
    @staticmethod
    def FromGiga(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromKilo(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromMega(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromMicro(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromMilli(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromNano(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromPico(significant: int) -> MeasuringRange: ...
    @staticmethod
    def FromTera(significant: int) -> MeasuringRange: ...
    def GetHashCode(self) -> int: ...
    def IsInRange(self, lowerBound: MeasuringRange, upperBound: MeasuringRange) -> bool: ...
    def NextLargerOrder(self) -> MeasuringRange: ...
    def NextSmallerOrder(self) -> MeasuringRange: ...
    def __eq__(self, lhs: MeasuringRange, rhs: MeasuringRange) -> bool: ...
    def __gt__(self, lhs: MeasuringRange, rhs: MeasuringRange) -> bool: ...
    def __ge__(self, lhs: MeasuringRange, rhs: MeasuringRange) -> bool: ...
    def __ne__(self, lhs: MeasuringRange, rhs: MeasuringRange) -> bool: ...
    def __lt__(self, lhs: MeasuringRange, rhs: MeasuringRange) -> bool: ...
    def __le__(self, lhs: MeasuringRange, rhs: MeasuringRange) -> bool: ...
    @staticmethod
    def Parse(source: str) -> MeasuringRange: ...
    def ToDecimal(self) -> Decimal: ...
    def ToDouble(self) -> float: ...
    def ToString(self) -> str: ...
    @staticmethod
    def TryParse(source: str, measuringRange: clr.Reference[MeasuringRange]) -> bool: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: MeasuringRange) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class MicroAmpere(IEquatable_1[MicroAmpere], IComparable_1[MicroAmpere]):
    def __init__(self, microAmperes: float) -> None: ...
    @property
    def Value(self) -> float: ...
    def CompareTo(self, other: MicroAmpere) -> int: ...
    @staticmethod
    def FromAmperes(amperes: float) -> MicroAmpere: ...
    def GetHashCode(self) -> int: ...
    def __add__(self, a: MicroAmpere, b: MicroAmpere) -> MicroAmpere: ...
    def __eq__(self, left: MicroAmpere, right: MicroAmpere) -> bool: ...
    # Operator not supported op_Implicit(microAmperes: Double)
    # Operator not supported op_Implicit(current: MicroAmpere)
    def __ne__(self, left: MicroAmpere, right: MicroAmpere) -> bool: ...
    def __sub__(self, a: MicroAmpere, b: MicroAmpere) -> MicroAmpere: ...
    def ToAmperes(self) -> float: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: MicroAmpere) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class PADMode(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    DC : PADMode # 0
    Pulse : PADMode # 1
    Differential : PADMode # 2


class PeakType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Auto : PeakType # 0
    Manual : PeakType # 1


class PotentialRange(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    pr1mV : PotentialRange # 0
    pr10mV : PotentialRange # 1
    pr20mV : PotentialRange # 2
    pr50mV : PotentialRange # 3
    pr100mV : PotentialRange # 4
    pr200mV : PotentialRange # 5
    pr500mV : PotentialRange # 6
    pr1V : PotentialRange # 7


class Prefix(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    None_ : Prefix # 0
    Deca : Prefix # 1
    Hecto : Prefix # 2
    Kilo : Prefix # 3
    Mega : Prefix # 6
    Giga : Prefix # 9
    Tera : Prefix # 12
    Peta : Prefix # 15
    Exa : Prefix # 18
    Zetta : Prefix # 21
    Yotta : Prefix # 24
    Ronna : Prefix # 27
    Quetta : Prefix # 30
    Quecto : Prefix # -30
    Ronto : Prefix # -27
    Yocto : Prefix # -24
    Zepto : Prefix # -21
    Atto : Prefix # -18
    Femto : Prefix # -15
    Pico : Prefix # -12
    Nano : Prefix # -9
    Micro : Prefix # -6
    Milli : Prefix # -3
    Centi : Prefix # -2
    Deci : Prefix # -1


class Quantity(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Capacitance : Quantity # 0
    Charge : Quantity # 1
    Conductance : Quantity # 2
    Current : Quantity # 3
    Frequency : Quantity # 4
    Potential : Quantity # 5
    Resistance : Quantity # 6
    Time : Quantity # 7
    Temperature : Quantity # 8
    Ordinal : Quantity # 9
    Angle : Quantity # 10
    Percentage : Quantity # 11
    TimePerPotential : Quantity # 12
    PotentialPerTime : Quantity # 13
    Custom : Quantity # 14


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


class Second(IEquatable_1[Second], IComparable_1[Second]):
    def __init__(self, seconds: float) -> None: ...
    @property
    def TotalSeconds(self) -> float: ...
    @property
    def Value(self) -> float: ...
    @classmethod
    @property
    def Zero(cls) -> Second: ...
    def CompareTo(self, other: Second) -> int: ...
    @staticmethod
    def FromSeconds(seconds: float) -> Second: ...
    def GetHashCode(self) -> int: ...
    def __add__(self, a: Second, b: Second) -> Second: ...
    def __truediv__(self, a: Second, divisor: float) -> Second: ...
    def __eq__(self, left: Second, right: Second) -> bool: ...
    # Operator not supported op_Implicit(seconds: Double)
    # Operator not supported op_Implicit(second: Second)
    def __ne__(self, left: Second, right: Second) -> bool: ...
    def __mul__(self, a: Second, factor: float) -> Second: ...
    def __sub__(self, a: Second, b: Second) -> Second: ...
    def ToString(self) -> str: ...
    def ToTimeSpan(self) -> TimeSpan: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: Second) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...



class TimeUnitType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    None_ : TimeUnitType # 0
    Second : TimeUnitType # 1
    Minute : TimeUnitType # 2
    Hour : TimeUnitType # 3
    Day : TimeUnitType # 4
    Week : TimeUnitType # 5
    Year : TimeUnitType # 6


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


class Volt(IEquatable_1[Volt], IComparable_1[Volt]):
    def __init__(self, volts: float) -> None: ...
    @property
    def Value(self) -> float: ...
    @classmethod
    @property
    def Zero(cls) -> Volt: ...
    def CompareTo(self, other: Volt) -> int: ...
    def GetHashCode(self) -> int: ...
    def __add__(self, a: Volt, b: Volt) -> Volt: ...
    def __eq__(self, left: Volt, right: Volt) -> bool: ...
    # Operator not supported op_Implicit(volts: Double)
    # Operator not supported op_Implicit(potential: Volt)
    def __ne__(self, left: Volt, right: Volt) -> bool: ...
    def __sub__(self, a: Volt, b: Volt) -> Volt: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: Volt) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...
