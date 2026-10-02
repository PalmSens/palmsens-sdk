import typing, clr, abc
from PalmSens.Sdk.Data.Models.Domain.Values import AxisDataTypeVariant
from PalmSens.Sdk.Data.Models.Entities.Method import Unit, Method, Parameter
from PalmSens.Sdk.Data.Models.Domain import CustomUnit, ITechniqueParameters
from System.Collections.Generic import IReadOnlyList_1, List_1, ICollection_1, IEnumerable_1
from PalmSens.Sdk.Data.Models.Domain.Data import CurveTemplate
from PalmSens.Sdk.Data.Models.Domain.TechniqueParameters import BiPotMode
from PalmSens import Method
from PalmSens.Sdk.Data.Models.Entities import TechniqueId
from PalmSens.Sdk.Data.Models.Dtos.Method import MethodParameter
from System import DateTimeOffset, Array_1, Func_2

class AxisDataTypeVariantExtensions(abc.ABC):
    @staticmethod
    def DisplayNegativeValues(axisDataType: AxisDataTypeVariant) -> bool: ...
    @staticmethod
    def GetAssociatedUnit(axisDataType: AxisDataTypeVariant, customUnit: CustomUnit = ...) -> Unit: ...
    @staticmethod
    def GetAssociatedUnitScaleFactor(axisDataType: AxisDataTypeVariant) -> float: ...


class MethodExtensions(abc.ABC):
    @staticmethod
    def AddCurveTemplatesParameter(method: Method, curveTemplates: IReadOnlyList_1[CurveTemplate]) -> None: ...
    @staticmethod
    def AddLabelsParameter(method: Method, labels: IReadOnlyList_1[str]) -> None: ...
    @staticmethod
    def AddNotesParameter(method: Method, notes: str) -> None: ...
    @staticmethod
    def FromLegacyBiPotMode(legacyMode: Method.EnumPalmSensBipotMode) -> BiPotMode: ...
    @staticmethod
    def FromLegacyMethodId(legacyTechnique: str) -> TechniqueId: ...
    @staticmethod
    def GetParametersCurveTemplates(legacyMethod: Method, technique: TechniqueId) -> List_1[CurveTemplate]: ...
    @staticmethod
    def SetWithParametersFrom(method: Method, methodParameterResults: ICollection_1[MethodParameter]) -> None: ...
    @staticmethod
    def SmoothLevelToString(smoothLevel: int) -> str: ...
    @staticmethod
    def SmoothLevelToWindowSize(smoothLevel: int) -> int: ...
    @staticmethod
    def ToEntity(techniqueParameters: ITechniqueParameters, name: str, notes: str, labels: IReadOnlyList_1[str], curveTemplates: IReadOnlyList_1[CurveTemplate], createdOn: DateTimeOffset) -> Method: ...
    @staticmethod
    def ToLegacyMethod(techniqueParameters: ITechniqueParameters) -> Method: ...
    @staticmethod
    def ToMethodParameters(legacyMethod: Method) -> ITechniqueParameters: ...


class MethodParametersExtensions(abc.ABC):
    @staticmethod
    def GetParameter(methodEntity: Method, parameterId: str) -> Parameter: ...
    @staticmethod
    def GetParameterGroupItemType(parameters: IEnumerable_1[Parameter]) -> str: ...
    @staticmethod
    def GetParameterThatEndsWith(parameters: IEnumerable_1[Parameter], str: str) -> Parameter: ...
    @staticmethod
    def ToParameterJsonArrayValue(value: typing.Any) -> str: ...
    @staticmethod
    def ToParameterValue(value: typing.Any) -> str: ...
    @staticmethod
    def TryGetParameterThatEndsWith(parameters: IEnumerable_1[Parameter], str: str, parameter: clr.Reference[Parameter]) -> bool: ...
    @staticmethod
    def ValueStringToObject(parameter: Parameter, propertyType: typing.Type[typing.Any]) -> typing.Any: ...
    # Skipped AddParameter due to it being static, abstract and generic.

    AddParameter : AddParameter_MethodGroup
    class AddParameter_MethodGroup:
        def __getitem__(self, t:typing.Type[AddParameter_1_T1]) -> AddParameter_1[AddParameter_1_T1]: ...

        AddParameter_1_T1 = typing.TypeVar('AddParameter_1_T1')
        class AddParameter_1(typing.Generic[AddParameter_1_T1]):
            AddParameter_1_T = MethodParametersExtensions.AddParameter_MethodGroup.AddParameter_1_T1
            def __call__(self, method: Method, parameterId: str, value: AddParameter_1_T) -> None:...


    # Skipped AddParameterIfNotNull due to it being static, abstract and generic.

    AddParameterIfNotNull : AddParameterIfNotNull_MethodGroup
    class AddParameterIfNotNull_MethodGroup:
        def __getitem__(self, t:typing.Type[AddParameterIfNotNull_1_T1]) -> AddParameterIfNotNull_1[AddParameterIfNotNull_1_T1]: ...

        AddParameterIfNotNull_1_T1 = typing.TypeVar('AddParameterIfNotNull_1_T1')
        class AddParameterIfNotNull_1(typing.Generic[AddParameterIfNotNull_1_T1]):
            AddParameterIfNotNull_1_T = MethodParametersExtensions.AddParameterIfNotNull_MethodGroup.AddParameterIfNotNull_1_T1
            def __call__(self, method: Method, parameterId: str, nullableValue: AddParameterIfNotNull_1_T) -> None:...


    # Skipped GetOptionalValue due to it being static, abstract and generic.

    GetOptionalValue : GetOptionalValue_MethodGroup
    class GetOptionalValue_MethodGroup:
        def __getitem__(self, t:typing.Type[GetOptionalValue_1_T1]) -> GetOptionalValue_1[GetOptionalValue_1_T1]: ...

        GetOptionalValue_1_T1 = typing.TypeVar('GetOptionalValue_1_T1')
        class GetOptionalValue_1(typing.Generic[GetOptionalValue_1_T1]):
            GetOptionalValue_1_T = MethodParametersExtensions.GetOptionalValue_MethodGroup.GetOptionalValue_1_T1
            def __call__(self, entity: Method, parameterId: str) -> typing.Optional[GetOptionalValue_1_T]:...


    # Skipped GetOptionalValueWithUse due to it being static, abstract and generic.

    GetOptionalValueWithUse : GetOptionalValueWithUse_MethodGroup
    class GetOptionalValueWithUse_MethodGroup:
        def __getitem__(self, t:typing.Type[GetOptionalValueWithUse_1_T1]) -> GetOptionalValueWithUse_1[GetOptionalValueWithUse_1_T1]: ...

        GetOptionalValueWithUse_1_T1 = typing.TypeVar('GetOptionalValueWithUse_1_T1')
        class GetOptionalValueWithUse_1(typing.Generic[GetOptionalValueWithUse_1_T1]):
            GetOptionalValueWithUse_1_T = MethodParametersExtensions.GetOptionalValueWithUse_MethodGroup.GetOptionalValueWithUse_1_T1
            def __call__(self, entity: Method, parameterId: str) -> typing.Optional[GetOptionalValueWithUse_1_T]:...


    # Skipped GetValue due to it being static, abstract and generic.

    GetValue : GetValue_MethodGroup
    class GetValue_MethodGroup:
        def __getitem__(self, t:typing.Type[GetValue_1_T1]) -> GetValue_1[GetValue_1_T1]: ...

        GetValue_1_T1 = typing.TypeVar('GetValue_1_T1')
        class GetValue_1(typing.Generic[GetValue_1_T1]):
            GetValue_1_T = MethodParametersExtensions.GetValue_MethodGroup.GetValue_1_T1
            @typing.overload
            def __call__(self, parameter: Parameter) -> GetValue_1_T:...
            @typing.overload
            def __call__(self, entity: Method, parameterId: str) -> GetValue_1_T:...


    # Skipped GetValues due to it being static, abstract and generic.

    GetValues : GetValues_MethodGroup
    class GetValues_MethodGroup:
        def __getitem__(self, t:typing.Type[GetValues_1_T1]) -> GetValues_1[GetValues_1_T1]: ...

        GetValues_1_T1 = typing.TypeVar('GetValues_1_T1')
        class GetValues_1(typing.Generic[GetValues_1_T1]):
            GetValues_1_T = MethodParametersExtensions.GetValues_MethodGroup.GetValues_1_T1
            def __call__(self, parameter: Parameter) -> Array_1[GetValues_1_T]:...


    # Skipped TransferItems due to it being static, abstract and generic.

    TransferItems : TransferItems_MethodGroup
    class TransferItems_MethodGroup:
        def __getitem__(self, t:typing.Type[TransferItems_1_T1]) -> TransferItems_1[TransferItems_1_T1]: ...

        TransferItems_1_T1 = typing.TypeVar('TransferItems_1_T1')
        class TransferItems_1(typing.Generic[TransferItems_1_T1]):
            TransferItems_1_T = MethodParametersExtensions.TransferItems_MethodGroup.TransferItems_1_T1
            def __call__(self, methodEntity: Method, parameterName: str, selector: Func_2[IEnumerable_1[Parameter], TransferItems_1_T]) -> IEnumerable_1[TransferItems_1_T]:...


    # Skipped TryGetValue due to it being static, abstract and generic.

    TryGetValue : TryGetValue_MethodGroup
    class TryGetValue_MethodGroup:
        def __getitem__(self, t:typing.Type[TryGetValue_1_T1]) -> TryGetValue_1[TryGetValue_1_T1]: ...

        TryGetValue_1_T1 = typing.TypeVar('TryGetValue_1_T1')
        class TryGetValue_1(typing.Generic[TryGetValue_1_T1]):
            TryGetValue_1_T = MethodParametersExtensions.TryGetValue_MethodGroup.TryGetValue_1_T1
            def __call__(self, entity: Method, parameterId: str, value: clr.Reference[TryGetValue_1_T]) -> bool:...




class TechniqueParametersMappers(abc.ABC):
    @staticmethod
    def ToEntity(methodModel: ITechniqueParameters) -> Method: ...
    @staticmethod
    def ToTechniqueParameters(methodEntity: Method) -> ITechniqueParameters: ...
