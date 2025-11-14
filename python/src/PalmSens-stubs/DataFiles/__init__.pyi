import typing, clr, abc
from PalmSens import Measurement, Method, ScanMethod, TimeMethod
from System.IO import Stream, StreamReader, TextWriter, StreamWriter
from System.Text import Encoding
from System import Array_1, Exception, Version, IProgress_1
from PalmSens.Plottables import EISData, Curve
from System.Collections.Generic import Dictionary_2, List_1, IDictionary_2, ICollection_1, KeyValuePair_2, IEnumerator_1, IEnumerable_1
from System.Data import DataTable
from System.Threading.Tasks import Task_1, Task
from System.Collections import IDictionary
from System.Reflection import MethodBase
from System.Threading import CancellationToken

class AnalysisMeasurementFile(MeasurementFile):
    @typing.overload
    def __init__(self, m: Measurement) -> None: ...
    @typing.overload
    def __init__(self, m: Method, fileStream: Stream) -> None: ...
    Measurement : Measurement
    def Load(self, fileStream: Stream) -> None: ...
    def Save(self, fileStream: Stream) -> None: ...


class CSVDataFile(DataFile):
    def __init__(self) -> None: ...

    class EnumEISDataColumns(typing.SupportsInt):
        @typing.overload
        def __init__(self, value : int) -> None: ...
        @typing.overload
        def __init__(self, value : int, force_if_true: bool) -> None: ...
        def __int__(self) -> int: ...

        # Values:
        Freq : CSVDataFile.EnumEISDataColumns # 1
        Logf : CSVDataFile.EnumEISDataColumns # 2
        Phase : CSVDataFile.EnumEISDataColumns # 4
        Idc : CSVDataFile.EnumEISDataColumns # 8
        Z : CSVDataFile.EnumEISDataColumns # 16
        ZRe : CSVDataFile.EnumEISDataColumns # 32
        ZIm : CSVDataFile.EnumEISDataColumns # 64
        LogZ : CSVDataFile.EnumEISDataColumns # 128
        Y : CSVDataFile.EnumEISDataColumns # 256
        YRe : CSVDataFile.EnumEISDataColumns # 512
        YIm : CSVDataFile.EnumEISDataColumns # 1024
        LogY : CSVDataFile.EnumEISDataColumns # 2048
        Cs : CSVDataFile.EnumEISDataColumns # 4096
        CR : CSVDataFile.EnumEISDataColumns # 8192
        Time : CSVDataFile.EnumEISDataColumns # 16384
        mEdc : CSVDataFile.EnumEISDataColumns # 32768
        Eac : CSVDataFile.EnumEISDataColumns # 65536
        Iac : CSVDataFile.EnumEISDataColumns # 131072
        AuxInput : CSVDataFile.EnumEISDataColumns # 262144
        CsRe : CSVDataFile.EnumEISDataColumns # 524288
        CsIm : CSVDataFile.EnumEISDataColumns # 1048576

    ColumnsForEIS : CSVDataFile.EnumEISDataColumns
    DefaultEISDataColumns : CSVDataFile.EnumEISDataColumns
    DialogFilter : str
    FileExtension : str
    @classmethod
    @property
    def CsvEncoding(cls) -> Encoding: ...
    @classmethod
    @property
    def CsvEncodingType(cls) -> EncodingType: ...
    @classmethod
    @CsvEncodingType.setter
    def CsvEncodingType(cls, value: EncodingType) -> EncodingType: ...
    @staticmethod
    def GetColumnNames(columns: CSVDataFile.EnumEISDataColumns) -> Array_1[str]: ...
    @staticmethod
    def GetRows(eisData: EISData, columns: CSVDataFile.EnumEISDataColumns) -> Array_1[str]: ...
    @staticmethod
    def SaveCurves(fileStream: Stream, curveData: Dictionary_2[Curve, Measurement], appendSessionFilePath: bool = ...) -> None: ...
    @staticmethod
    def SaveEISData(fileStream: Stream, eisDatas: Dictionary_2[Measurement, List_1[EISData]], columns: CSVDataFile.EnumEISDataColumns = ..., appendSessionFilePath: bool = ...) -> None: ...
    @staticmethod
    def SaveMeasurements(fileStream: Stream, dataTables: Dictionary_2[DataTable, Measurement], eisDataTables: Dictionary_2[DataTable, Measurement], appendSessionFilePath: bool = ...) -> None: ...


class CurveFile(DataFile):
    @typing.overload
    def __init__(self, c: Curve) -> None: ...
    @typing.overload
    def __init__(self, fileStream: StreamReader, method: Method, filepath: str) -> None: ...
    @typing.overload
    def __init__(self, fileStream: StreamReader, methodStream: StreamReader, methodFileType: MethodFileType, filepath: str) -> None: ...
    _curve : Curve
    FileDialogFilter : str
    FileExtensionScan : str
    FileExtensionTime : str
    Method : Method
    @property
    def Curve(self) -> Curve: ...
    # Skipped Save due to it being static, abstract and generic.

    Save : Save_MethodGroup
    class Save_MethodGroup:
        @typing.overload
        def __call__(self, fileStream: Stream, filename: str) -> None:...
        @typing.overload
        def __call__(self, fileStream: Stream, filename: str, changeTitle: bool) -> None:...
        @typing.overload
        def __call__(self, fileStream: Stream, filename: str, c: Curve, changeTitle: bool) -> None:...



class DataFile(abc.ABC):
    CRLF : str
    POLE : str
    SPACE : str
    TAB : str
    @classmethod
    @property
    def DefaultEncoding(cls) -> Encoding: ...


class EISAnalysisFile(abc.ABC):
    @staticmethod
    def Save(scan: EISData, fileStream: Stream) -> None: ...


class EISDataFile(DataFile):
    def __init__(self, fileStream: Stream) -> None: ...
    FileDialogFilter : str
    FileExtension : str
    @staticmethod
    def Deserialize(input: str) -> EISData: ...
    @staticmethod
    def DeserializeAsync(input: str) -> Task_1[EISData]: ...
    @staticmethod
    def EISDataFileAsync(fileStream: Stream) -> Task_1[EISDataFile]: ...
    @staticmethod
    def FromStream(fileStream: Stream) -> EISData: ...
    @staticmethod
    def Save(source: str, eisdata: EISData, fileStream: Stream, fileName: str) -> None: ...
    @staticmethod
    def Serialize(source: str, eisdata: EISData, contents: TextWriter) -> None: ...


class EncodingType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    UTF8BOM : EncodingType # 0
    UTF16LE : EncodingType # 1
    UTF16BE : EncodingType # 2
    UTF16LEBOM : EncodingType # 3
    UTF16BEBOM : EncodingType # 4
    UTF8 : EncodingType # 5


class InvalidJsonException(Exception):
    def __init__(self, message: str) -> None: ...
    @property
    def Data(self) -> IDictionary: ...
    @property
    def HelpLink(self) -> str: ...
    @HelpLink.setter
    def HelpLink(self, value: str) -> str: ...
    @property
    def HResult(self) -> int: ...
    @HResult.setter
    def HResult(self, value: int) -> int: ...
    @property
    def InnerException(self) -> Exception: ...
    @property
    def Message(self) -> str: ...
    @property
    def Source(self) -> str: ...
    @Source.setter
    def Source(self, value: str) -> str: ...
    @property
    def StackTrace(self) -> str: ...
    @property
    def TargetSite(self) -> MethodBase: ...


class JsonBag(IDictionary_2[str, typing.Any]):
    def __init__(self) -> None: ...
    Empty : JsonBag
    @property
    def Count(self) -> int: ...
    @property
    def IsReadOnly(self) -> bool: ...
    @property
    def Item(self) -> typing.Any: ...
    @Item.setter
    def Item(self, value: typing.Any) -> typing.Any: ...
    @property
    def Keys(self) -> ICollection_1[str]: ...
    @property
    def Values(self) -> ICollection_1[typing.Any]: ...
    def Clear(self) -> None: ...
    def Contains(self, item: KeyValuePair_2[str, typing.Any]) -> bool: ...
    def ContainsKey(self, key: str) -> bool: ...
    def CopyTo(self, array: Array_1[KeyValuePair_2[str, typing.Any]], arrayIndex: int) -> None: ...
    def GetEnumerator(self) -> IEnumerator_1[KeyValuePair_2[str, typing.Any]]: ...
    def TryGetValue(self, key: str, value: clr.Reference[typing.Any]) -> bool: ...
    # Skipped Add due to it being static, abstract and generic.

    Add : Add_MethodGroup
    class Add_MethodGroup:
        @typing.overload
        def __call__(self, item: KeyValuePair_2[str, typing.Any]) -> None:...
        @typing.overload
        def __call__(self, key: str, value: typing.Any) -> None:...

    # Skipped GetValue due to it being static, abstract and generic.

    GetValue : GetValue_MethodGroup
    class GetValue_MethodGroup:
        def __getitem__(self, t:typing.Type[GetValue_1_T1]) -> GetValue_1[GetValue_1_T1]: ...

        GetValue_1_T1 = typing.TypeVar('GetValue_1_T1')
        class GetValue_1(typing.Generic[GetValue_1_T1]):
            GetValue_1_T = JsonBag.GetValue_MethodGroup.GetValue_1_T1
            def __call__(self, key: str) -> GetValue_1_T:...


    # Skipped GetValueArray due to it being static, abstract and generic.

    GetValueArray : GetValueArray_MethodGroup
    class GetValueArray_MethodGroup:
        def __getitem__(self, t:typing.Type[GetValueArray_1_T1]) -> GetValueArray_1[GetValueArray_1_T1]: ...

        GetValueArray_1_T1 = typing.TypeVar('GetValueArray_1_T1')
        class GetValueArray_1(typing.Generic[GetValueArray_1_T1]):
            GetValueArray_1_T = JsonBag.GetValueArray_MethodGroup.GetValueArray_1_T1
            def __call__(self, key: str) -> Array_1[GetValueArray_1_T]:...


    # Skipped Remove due to it being static, abstract and generic.

    Remove : Remove_MethodGroup
    class Remove_MethodGroup:
        @typing.overload
        def __call__(self, item: KeyValuePair_2[str, typing.Any]) -> bool:...
        @typing.overload
        def __call__(self, key: str) -> bool:...



class JsonParser:
    def __init__(self) -> None: ...
    @staticmethod
    def FromJsonAsync(json: str, cancellationToken: CancellationToken) -> Task_1[JsonBag]: ...
    @staticmethod
    def IsFloatingPoint(value: typing.Any) -> bool: ...
    @staticmethod
    def IsInteger(value: typing.Any) -> bool: ...
    @staticmethod
    def ToJson(sw: StreamWriter, bag: JsonBag) -> None: ...
    @staticmethod
    def ToJsonAsync(sw: StreamWriter, bag: JsonBag, cancellationToken: CancellationToken) -> Task: ...
    # Skipped FromJson due to it being static, abstract and generic.

    FromJson : FromJson_MethodGroup
    class FromJson_MethodGroup:
        @typing.overload
        def __call__(self, json: str) -> JsonBag:...
        @typing.overload
        def __call__(self, json: str, type: clr.Reference[JsonToken]) -> JsonBag:...



class JsonToken(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    Unknown : JsonToken # 0
    LeftBrace : JsonToken # 1
    RightBrace : JsonToken # 2
    Colon : JsonToken # 3
    Comma : JsonToken # 4
    LeftBracket : JsonToken # 5
    RightBracket : JsonToken # 6
    String : JsonToken # 7
    Number : JsonToken # 8
    True : JsonToken # 9
    False : JsonToken # 10
    Null : JsonToken # 11
    NaN : JsonToken # 12


class MeasurementFile(DataFile):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, mm: Measurement) -> None: ...
    Measurement : Measurement


class MethodFile(DataFile):
    EField : Array_1[str]
    ELabel : Array_1[str]
    EMax : Array_1[float]
    EMin : Array_1[float]
    EUnit : Array_1[str]
    Filename : str
    HandleAsCorrosionMethod : bool
    LabelX : str
    LabelY : str
    tField : Array_1[str]
    tLabel : Array_1[str]
    tMax : Array_1[float]
    tMin : Array_1[float]
    tUnit : Array_1[str]
    @property
    def Method(self) -> Method: ...
    @Method.setter
    def Method(self, value: Method) -> Method: ...
    @classmethod
    @property
    def ScanMethodExtension(cls) -> str: ...
    @property
    def Technique(self) -> int: ...
    @classmethod
    @property
    def TimeMethodExtension(cls) -> str: ...
    def Equals(self, o: typing.Any) -> bool: ...
    def get_EValue(self, i: int) -> float: ...
    def get_tValue(self, i: int) -> float: ...
    def GetHashCode(self) -> int: ...
    def GetMethodData(self, name: str) -> float: ...
    @staticmethod
    def LoadAnyMethodFile(file: StreamReader, fileName: str, isCorrosion: bool) -> Method: ...
    @abc.abstractmethod
    def Save(self, filename: str) -> None: ...
    def set_EValue(self, i: int, Value: float) -> None: ...
    def set_tValue(self, i: int, Value: float) -> None: ...
    # Skipped FromStream due to it being static, abstract and generic.

    FromStream : FromStream_MethodGroup
    class FromStream_MethodGroup:
        @typing.overload
        def __call__(self, file: StreamReader, filename: str) -> MethodFile:...
        @typing.overload
        def __call__(self, fileStream: StreamReader, fileName: str, includeCorrosionVars: bool) -> MethodFile:...

    # Skipped FromTechnique due to it being static, abstract and generic.

    FromTechnique : FromTechnique_MethodGroup
    class FromTechnique_MethodGroup:
        @typing.overload
        def __call__(self, i: int) -> MethodFile:...
        @typing.overload
        def __call__(self, method: Method) -> MethodFile:...
        @typing.overload
        def __call__(self, i: int, includeCorrosionVars: bool) -> MethodFile:...

    # Skipped SetMethodData due to it being static, abstract and generic.

    SetMethodData : SetMethodData_MethodGroup
    class SetMethodData_MethodGroup:
        @typing.overload
        def __call__(self, name: str, data: float) -> None:...
        @typing.overload
        def __call__(self, name: str, data: float, index: int) -> None:...



class MethodFile2(abc.ABC):
    DialogFilter : str
    FileExtension : str
    @staticmethod
    def Deserialize(contents: str) -> Method: ...
    @staticmethod
    def FromStream(file: StreamReader) -> Method: ...
    @staticmethod
    def Save(method: Method, fileStream: Stream, filepath: str, changeTitle: bool, sourceApllication: str = ..., sourceApplicationVersion: str = ...) -> None: ...
    @staticmethod
    def Serialize(method: Method, tw: TextWriter, sourceApplication: str = ..., sourceApplicationVersion: str = ...) -> None: ...
    @staticmethod
    def SerializeAsync(method: Method, tw: TextWriter, cancellationToken: CancellationToken, sourceApplication: str = ..., sourceApplicationVersion: str = ...) -> Task: ...


class MethodFileType(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...

    # Values:
    MethodFileOldPms : MethodFileType # 0
    MethodFileOldPmt : MethodFileType # 1
    MethodFile2 : MethodFileType # 2


class MuxMeasurementFile(MeasurementFile):
    def __init__(self, m: Method, fileStream: StreamReader) -> None: ...
    FileExtension : str
    Measurement : Measurement
    @staticmethod
    def FromStream(measurementStream: StreamReader, methodStream: StreamReader) -> Measurement: ...
    def Load(self, fileStream: StreamReader) -> None: ...
    @staticmethod
    def Save(fileStream: Stream, curveArray: Array_1[Curve], method: Method, saveEcorrectedValues: bool = ...) -> None: ...


class PartialLoadException_GenericClasses(abc.ABCMeta):
    Generic_PartialLoadException_GenericClasses_PartialLoadException_1_T = typing.TypeVar('Generic_PartialLoadException_GenericClasses_PartialLoadException_1_T')
    def __getitem__(self, types : typing.Type[Generic_PartialLoadException_GenericClasses_PartialLoadException_1_T]) -> typing.Type[PartialLoadException_1[Generic_PartialLoadException_GenericClasses_PartialLoadException_1_T]]: ...

PartialLoadException : PartialLoadException_GenericClasses

PartialLoadException_1_T = typing.TypeVar('PartialLoadException_1_T')
class PartialLoadException_1(typing.Generic[PartialLoadException_1_T], Exception):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, partiallyLoadedObject: PartialLoadException_1_T) -> None: ...
    @typing.overload
    def __init__(self, partiallyLoadedPartiallyLoadedObjectArray: IEnumerable_1[PartialLoadException_1_T]) -> None: ...
    PartiallyLoadedObject : PartialLoadException_1_T
    PartiallyLoadedObjectArray : IEnumerable_1[PartialLoadException_1_T]
    @property
    def Data(self) -> IDictionary: ...
    @property
    def HelpLink(self) -> str: ...
    @HelpLink.setter
    def HelpLink(self, value: str) -> str: ...
    @property
    def HResult(self) -> int: ...
    @HResult.setter
    def HResult(self, value: int) -> int: ...
    @property
    def InnerException(self) -> Exception: ...
    @property
    def Message(self) -> str: ...
    @property
    def Source(self) -> str: ...
    @Source.setter
    def Source(self, value: str) -> str: ...
    @property
    def StackTrace(self) -> str: ...
    @property
    def TargetSite(self) -> MethodBase: ...


class ScanMethodFile(MethodFile):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, fileStream: StreamReader, fileName: str) -> None: ...
    @typing.overload
    def __init__(self, fileStream: StreamReader, fileName: str, handleAsCorrosionMethod: bool) -> None: ...
    @typing.overload
    def __init__(self, scanmethod: ScanMethod) -> None: ...
    @typing.overload
    def __init__(self, scanmethod: ScanMethod, includeCorrosionVars: bool) -> None: ...
    EField : Array_1[str]
    ELabel : Array_1[str]
    EMax : Array_1[float]
    EMin : Array_1[float]
    EUnit : Array_1[str]
    Filename : str
    HandleAsCorrosionMethod : bool
    LabelX : str
    LabelY : str
    tField : Array_1[str]
    tLabel : Array_1[str]
    tMax : Array_1[float]
    tMin : Array_1[float]
    tUnit : Array_1[str]
    @property
    def Method(self) -> Method: ...
    @Method.setter
    def Method(self, value: Method) -> Method: ...
    @property
    def ScanMethod(self) -> ScanMethod: ...
    @ScanMethod.setter
    def ScanMethod(self, value: ScanMethod) -> ScanMethod: ...
    @property
    def Technique(self) -> int: ...
    def Save(self, strFilename: str) -> None: ...


class SessionFile(DataFile):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, measurements: Array_1[Measurement], methodForEditor: Method, metaData: JsonBag) -> None: ...
    CoreVersion : Version
    FileExtension : str
    Measurements : Array_1[Measurement]
    MetaData : JsonBag
    MethodForEditor : Method
    def Load(self, fileStream: Stream) -> None: ...
    def LoadAsync(self, fileStream: Stream, cancellationToken: CancellationToken) -> Task: ...
    def Save(self, fileStream: Stream, filePath: str, setSavedToField: bool = ...) -> None: ...
    def SaveAsync(self, fileStream: Stream, filePath: str, cancellationToken: CancellationToken, progress: IProgress_1[bool], setSavedToField: bool = ...) -> Task: ...


class TimeMethodFile(MethodFile):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, fileStream: StreamReader, fileName: str) -> None: ...
    @typing.overload
    def __init__(self, fileStream: StreamReader, fileName: str, handleAsCorrosionMethod: bool) -> None: ...
    @typing.overload
    def __init__(self, timemethod: TimeMethod) -> None: ...
    @typing.overload
    def __init__(self, timemethod: TimeMethod, handleAsCorrosionMethod: bool) -> None: ...
    EField : Array_1[str]
    ELabel : Array_1[str]
    EMax : Array_1[float]
    EMin : Array_1[float]
    EUnit : Array_1[str]
    Filename : str
    HandleAsCorrosionMethod : bool
    LabelX : str
    LabelY : str
    tField : Array_1[str]
    tLabel : Array_1[str]
    tMax : Array_1[float]
    tMin : Array_1[float]
    tUnit : Array_1[str]
    @property
    def Method(self) -> Method: ...
    @Method.setter
    def Method(self, value: Method) -> Method: ...
    @property
    def Technique(self) -> int: ...
    @property
    def TimeMethod(self) -> TimeMethod: ...
    @TimeMethod.setter
    def TimeMethod(self, value: TimeMethod) -> TimeMethod: ...
    def Save(self, strFilename: str) -> None: ...
