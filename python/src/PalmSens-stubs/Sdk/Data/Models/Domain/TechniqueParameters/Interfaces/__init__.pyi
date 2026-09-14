import typing, clr, abc
from PalmSens.Sdk.Data.Models.Domain.Values import CurrentRange, Volt, Second, CurrentIcr, PotentialRange
from PalmSens.Sdk.Data.Models.Domain.TechniqueParameters import BiPotMode
from PalmSens.Sdk.Data.Models.Domain.Values.Instruments import CellMode
from System.Collections.Generic import IReadOnlyList_1
from PalmSens.Sdk.Data.Models.Domain import MinMaxLimit, ITechniqueParameters
from System import Array_1, IEquatable_1

class IAppliedCurrentRangeParameters(typing.Protocol):
    @property
    def AppliedCurrentRange(self) -> CurrentRange: ...


class IAppliedPotentialParameters(typing.Protocol):
    @abc.abstractmethod
    def GetMinMaxAppliedPotential(self) -> MinMaxPotential: ...


class IBiPotParameters(typing.Protocol):
    @property
    def BiPotCurrentRange(self) -> typing.Optional[CurrentRange]: ...
    @property
    def BiPotMode(self) -> typing.Optional[BiPotMode]: ...
    @property
    def BiPotPotential(self) -> typing.Optional[Volt]: ...
    @property
    def IsBiPotOn(self) -> typing.Optional[bool]: ...


class IChargeLimitParameters(typing.Protocol):
    pass


class IConditioningParameters(typing.Protocol):
    @property
    def ConditioningPotential(self) -> Volt: ...
    @property
    def ConditioningTime(self) -> Second: ...


class ICurrentLimitParameters(typing.Protocol):
    pass


class ICurrentStepSweepParameters(typing.Protocol):
    @property
    def BeginCurrent(self) -> CurrentIcr: ...
    @property
    def EndCurrent(self) -> CurrentIcr: ...
    @property
    def StepCurrent(self) -> CurrentIcr: ...


class IDepositionParameters(typing.Protocol):
    @property
    def DepositionPotential(self) -> Volt: ...
    @property
    def DepositionTime(self) -> Second: ...


class IDropDetectionParameters(typing.Protocol):
    @property
    def EnableDropDetection(self) -> typing.Optional[bool]: ...


class IEnableCellAfterMeasurementParameters(typing.Protocol):
    @property
    def AppliedCurrentRangeAfterMeasurement(self) -> typing.Optional[CurrentRange]: ...
    @property
    def CellModeAfterMeasurement(self) -> CellMode: ...
    @property
    def CurrentAfterMeasurement(self) -> typing.Optional[CurrentIcr]: ...
    @property
    def EnableCellAfterMeasurement(self) -> bool: ...
    @property
    def MeasuredCurrentRangeAfterMeasurement(self) -> typing.Optional[CurrentRange]: ...
    @property
    def MeasuredPotentialRangeAfterMeasurement(self) -> typing.Optional[PotentialRange]: ...
    @property
    def PotentialAfterMeasurement(self) -> typing.Optional[Volt]: ...


class IEndPotentialParameters(typing.Protocol):
    @property
    def EndPotential(self) -> Volt: ...


class IEquilibrationParameters(typing.Protocol):
    @property
    def EquilibrationTime(self) -> Second: ...


class IFrequencyParameters(typing.Protocol):
    @property
    def Frequency(self) -> float: ...


class IGalvanostatic(typing.Protocol):
    @property
    def AppliedCurrentRange(self) -> CurrentRange: ...


class IHardwareSyncParameters(typing.Protocol):
    @property
    def HardwareSyncEnabled(self) -> typing.Optional[bool]: ...


class IImpedanceSpectroscopy(typing.Protocol):
    @property
    def NumberOfFrequencies(self) -> int: ...


class IIntervalTimeParameters(typing.Protocol):
    @property
    def IntervalTime(self) -> Second: ...


class IIrCompensationParameters(typing.Protocol):
    @property
    def EnableIrCompensation(self) -> typing.Optional[bool]: ...
    @property
    def IrCompensation(self) -> typing.Optional[float]: ...


class IMaximumFrequencyParameters(typing.Protocol):
    @property
    def MaximumFrequency(self) -> float: ...


class IMeasuredCurrentRangeParameters(typing.Protocol):
    pass


class IMeasuredPotentialRangeParameters(typing.Protocol):
    pass


class IMeasureForwardAndReverseCurrentParameters(typing.Protocol):
    @property
    def MeasureForwardAndReverseCurrent(self) -> bool: ...


class IMinMaxMeasuredCurrentRangeParameters(IMeasuredCurrentRangeParameters, typing.Protocol):
    @property
    def MaximumMeasuredCurrentRange(self) -> CurrentRange: ...
    @property
    def MinimumMeasuredCurrentRange(self) -> CurrentRange: ...
    @property
    def StartingMeasuredCurrentRange(self) -> CurrentRange: ...


class IMinMaxMeasuredPotentialRangeParameters(IMeasuredPotentialRangeParameters, typing.Protocol):
    @property
    def MaximumMeasuredPotentialRange(self) -> PotentialRange: ...
    @property
    def MinimumMeasuredPotentialRange(self) -> PotentialRange: ...
    @property
    def StartingMeasuredPotentialRange(self) -> PotentialRange: ...


class IMinMaxOptionalMeasuredPotentialRangeParameters(IMeasuredPotentialRangeParameters, typing.Protocol):
    @property
    def MaximumMeasuredPotentialRange(self) -> typing.Optional[PotentialRange]: ...
    @property
    def MinimumMeasuredPotentialRange(self) -> typing.Optional[PotentialRange]: ...
    @property
    def StartingMeasuredPotentialRange(self) -> typing.Optional[PotentialRange]: ...


class IMinMaxOptionalStartMeasuredCurrentRangeParameters(IMeasuredCurrentRangeParameters, typing.Protocol):
    @property
    def MaximumMeasuredCurrentRange(self) -> CurrentRange: ...
    @property
    def MinimumMeasuredCurrentRange(self) -> CurrentRange: ...
    @property
    def StartingMeasuredCurrentRange(self) -> typing.Optional[CurrentRange]: ...


class IMultistepLevel(typing.Protocol):
    @property
    def Duration(self) -> Second: ...
    @property
    def Record(self) -> bool: ...


class IMultistepParameters(IIntervalTimeParameters, typing.Protocol):
    @property
    def EnableRecordPerLevel(self) -> bool: ...
    @property
    def Levels(self) -> IReadOnlyList_1[IMultistepLevel]: ...
    @property
    def NumberOfCycles(self) -> int: ...


class IOptionalChargeLimitParameters(IChargeLimitParameters, typing.Protocol):
    @property
    def ChargeLimits(self) -> typing.Optional[MinMaxLimit]: ...


class IOptionalCurrentLimitParameters(ICurrentLimitParameters, typing.Protocol):
    @property
    def CurrentLimits(self) -> typing.Optional[MinMaxLimit]: ...


class IOptionalMinMaxPotentialRangeParameters(IMinMaxOptionalMeasuredPotentialRangeParameters, typing.Protocol):
    pass


class IOptionalPotentialLimitParameters(IPotentialLimitParameters, typing.Protocol):
    @property
    def PotentialLimits(self) -> typing.Optional[MinMaxLimit]: ...


class IOptionalRecordWeCurrentParameters(IRecordWeCurrentParameters, typing.Protocol):
    @property
    def RecordWeCurrent(self) -> typing.Optional[bool]: ...


class IPotentialLimitParameters(typing.Protocol):
    pass


class IPotentialSweep(IStepPotentialParameters, typing.Protocol):
    @property
    def BeginPotential(self) -> Volt: ...
    @property
    def EndPotential(self) -> Volt: ...


class IPotentiostatic(IPretreatable, IAppliedPotentialParameters, typing.Protocol):
    pass


class IPretreatable(IDepositionParameters, IConditioningParameters, typing.Protocol):
    def GetPretreatmentPotentials(self) -> Array_1[Volt]: ...


class IPulseTimeAndIntervalTimeParameters(IIntervalTimeParameters, IPulseTimeParameters, typing.Protocol):
    pass


class IPulseTimeParameters(typing.Protocol):
    @property
    def PulseTime(self) -> Second: ...


class IRecordAuxInputParameters(typing.Protocol):
    @property
    def RecordAuxInput(self) -> bool: ...


class IRecordCellPotentialParameters(typing.Protocol):
    @property
    def RecordCellPotential(self) -> typing.Optional[bool]: ...


class IRecordTimeDomainDataParameters(typing.Protocol):
    @property
    def RecordTimeDomainData(self) -> typing.Optional[bool]: ...


class IRecordWeCurrentParameters(typing.Protocol):
    pass


class IRecordWePotentialParameters(typing.Protocol):
    @property
    def RecordWePotential(self) -> typing.Optional[bool]: ...


class IRequiredChargeLimitParameters(IChargeLimitParameters, typing.Protocol):
    @property
    def ChargeLimits(self) -> MinMaxLimit: ...


class IRequiredCurrentLimitParameters(ICurrentLimitParameters, typing.Protocol):
    @property
    def CurrentLimits(self) -> MinMaxLimit: ...


class IRequiredPotentialLimitParameters(IPotentialLimitParameters, typing.Protocol):
    @property
    def PotentialLimits(self) -> MinMaxLimit: ...


class IRequiredRecordWeCurrentParameters(IRecordWeCurrentParameters, typing.Protocol):
    @property
    def RecordWeCurrent(self) -> bool: ...


class IReverseCurrentLimitParameters(typing.Protocol):
    @property
    def ReverseCurrentLimits(self) -> typing.Optional[MinMaxLimit]: ...


class IRuntimeAndIntervalTimeParameters(IIntervalTimeParameters, typing.Protocol):
    @property
    def RunTime(self) -> Second: ...


class IScanRateParameters(typing.Protocol):
    @property
    def ScanRate(self) -> float: ...


class ISingularMeasuredCurrentRangeParameter(IMeasuredCurrentRangeParameters, typing.Protocol):
    @property
    def MeasuredCurrentRange(self) -> CurrentRange: ...


class IStepCurrentAndScanRateParameters(IAppliedCurrentRangeParameters, typing.Protocol):
    @property
    def ScanRateInAmperePerSecond(self) -> float: ...
    @property
    def StepCurrent(self) -> CurrentIcr: ...


class IStepPotentialAndScanRateParameters(IScanRateParameters, IStepPotentialParameters, typing.Protocol):
    pass


class IStepPotentialParameters(typing.Protocol):
    @property
    def StepPotential(self) -> Volt: ...


class IVsOcpParameters(ITechniqueParameters, typing.Protocol):
    @property
    def MaximumOcpTime(self) -> Second: ...
    @property
    def MeasureVsOcp(self) -> bool: ...
    @property
    def OcpStabilityCriterion(self) -> float: ...


class MinMaxPotential(IEquatable_1[MinMaxPotential]):
    def __init__(self, Minimum: Volt, Maximum: Volt) -> None: ...
    @property
    def Maximum(self) -> Volt: ...
    @Maximum.setter
    def Maximum(self, value: Volt) -> Volt: ...
    @property
    def Minimum(self) -> Volt: ...
    @Minimum.setter
    def Minimum(self, value: Volt) -> Volt: ...
    @staticmethod
    def Create(args: Array_1[Volt]) -> MinMaxPotential: ...
    @staticmethod
    def CreateIncludingPretreatment(parameters: IPretreatable, potentials: Array_1[Volt]) -> MinMaxPotential: ...
    def Deconstruct(self, Minimum: clr.Reference[Volt], Maximum: clr.Reference[Volt]) -> None: ...
    def GetHashCode(self) -> int: ...
    def __eq__(self, left: MinMaxPotential, right: MinMaxPotential) -> bool: ...
    def __ne__(self, left: MinMaxPotential, right: MinMaxPotential) -> bool: ...
    def ToString(self) -> str: ...
    # Skipped Equals due to it being static, abstract and generic.

    Equals : Equals_MethodGroup
    class Equals_MethodGroup:
        @typing.overload
        def __call__(self, other: MinMaxPotential) -> bool:...
        @typing.overload
        def __call__(self, obj: typing.Any) -> bool:...
