import typing, clr, abc
from System import Array_1, ValueTuple_3, Func_2, IEquatable_1, IFormattable
from PalmSens.Plottables import Curve
from System.Collections.Generic import IList_1, List_1, Dictionary_2
from PalmSens.Data import EnumDirection, DataArray
from PalmSens import SineCurve
from System.Drawing import PointF

class DataManipulation(abc.ABC):
    @staticmethod
    def SmoothData(smoothLevel: int, yvalues: clr.Reference[Array_1[float]]) -> None: ...


class MathFunctions(abc.ABC):

    class enumOperator(typing.SupportsInt):
        @typing.overload
        def __init__(self, value : int) -> None: ...
        @typing.overload
        def __init__(self, value : int, force_if_true: bool) -> None: ...
        def __int__(self) -> int: ...

        # Values:
        Add : MathFunctions.enumOperator # 0
        Subtract : MathFunctions.enumOperator # 1

    @staticmethod
    def Abs(x: Array_1[float]) -> Array_1[float]: ...
    @staticmethod
    def AppendCurves(curveA: Curve, curveB: Curve) -> Curve: ...
    @staticmethod
    def AreDataArraysEqual(arrays: IList_1[Array_1[float]]) -> bool: ...
    @staticmethod
    def Average(arrays: IList_1[Array_1[float]]) -> IList_1[float]: ...
    @staticmethod
    def CalculateDerivative(dir: EnumDirection, y: Array_1[float], startIndex: int, endIndex: int, averagePoints: int) -> Array_1[float]: ...
    @staticmethod
    def ConvertFilteringModeToOffset(filterMode: int, nSamples: int) -> int: ...
    @staticmethod
    def Detrend(y: Array_1[float]) -> Array_1[float]: ...
    @staticmethod
    def DetrendFast(y: Array_1[float]) -> Array_1[float]: ...
    @staticmethod
    def DFT(sine: SineCurve, re: clr.Reference[float], im: clr.Reference[float]) -> None: ...
    @staticmethod
    def DivComplex(a: float, b: float, c: float, d: float, re: clr.Reference[float], im: clr.Reference[float]) -> None: ...
    @staticmethod
    def FindMeanY(c: Curve) -> float: ...
    @staticmethod
    def GetACRMS(sine: SineCurve, acRMS: clr.Reference[float]) -> None: ...
    @staticmethod
    def GetSpecifiedIndices(x: Array_1[float], indices: Array_1[int]) -> Array_1[float]: ...
    @staticmethod
    def IndexMin(x: Array_1[float]) -> int: ...
    @staticmethod
    def Linearity(y: Array_1[float], yRef: Array_1[float]) -> float: ...
    @staticmethod
    def Log10(y: Array_1[float]) -> Array_1[float]: ...
    @staticmethod
    def MultiplyDataArray(array: Array_1[float], factor: float) -> Array_1[float]: ...
    @staticmethod
    def NormalizeArray(array: Array_1[float], min: float, max: float) -> Array_1[float]: ...
    @staticmethod
    def Pow(y: Array_1[float], power: int) -> Array_1[float]: ...
    @staticmethod
    def RCHighPass(frequency: float, freq0: float, phaseshift: clr.Reference[float], Zfactor: clr.Reference[float]) -> None: ...
    @staticmethod
    def RCHighPassFreq0(frequency: float, phaseshift: float) -> float: ...
    @staticmethod
    def RCLowPass(frequency: float, freq0: float, phaseshift: clr.Reference[float], Zfactor: clr.Reference[float]) -> None: ...
    @staticmethod
    def RCLowPassFreq0(frequency: float, phaseshift: float) -> float: ...
    @staticmethod
    def SavitzkyGolay(smoothLevel: int, yvalues: clr.Reference[Array_1[float]], oldFormat: bool = ...) -> None: ...
    # Skipped Add due to it being static, abstract and generic.

    Add : Add_MethodGroup
    class Add_MethodGroup:
        @typing.overload
        def __call__(self, x: Array_1[float], val: float) -> Array_1[float]:...
        @typing.overload
        def __call__(self, x1: Array_1[float], x2: Array_1[float]) -> Array_1[float]:...

    # Skipped AddSubtractCurves due to it being static, abstract and generic.

    AddSubtractCurves : AddSubtractCurves_MethodGroup
    class AddSubtractCurves_MethodGroup:
        @typing.overload
        def __call__(self, curveA: Curve, curveB: Curve, Operator: MathFunctions.enumOperator) -> Curve:...
        @typing.overload
        def __call__(self, curveA: Curve, curveB: Curve, Operator: MathFunctions.enumOperator, iStart: int, iEnd: int) -> Curve:...

    # Skipped AddSubtractDataArrays due to it being static, abstract and generic.

    AddSubtractDataArrays : AddSubtractDataArrays_MethodGroup
    class AddSubtractDataArrays_MethodGroup:
        @typing.overload
        def __call__(self, dataA: Array_1[float], dataB: Array_1[float], Operator: MathFunctions.enumOperator) -> Array_1[float]:...
        @typing.overload
        def __call__(self, dataA: DataArray, dataB: DataArray, Operator: MathFunctions.enumOperator) -> DataArray:...
        @typing.overload
        def __call__(self, dataA: Array_1[float], dataB: Array_1[float], Operator: MathFunctions.enumOperator, iAStart: int, iBStart: int, count: int) -> Array_1[float]:...

    # Skipped FitLine due to it being static, abstract and generic.

    FitLine : FitLine_MethodGroup
    class FitLine_MethodGroup:
        @typing.overload
        def __call__(self, x: Array_1[float], y: Array_1[float]) -> Array_1[float]:...
        @typing.overload
        def __call__(self, range: int, index: int, x: Array_1[float], y: Array_1[float]) -> Array_1[float]:...

    # Skipped FitLine2 due to it being static, abstract and generic.

    FitLine2 : FitLine2_MethodGroup
    class FitLine2_MethodGroup:
        @typing.overload
        def __call__(self, x: Array_1[float], y: Array_1[float]) -> ValueTuple_3[float, float, float]:...
        @typing.overload
        def __call__(self, range: int, index: int, x: Array_1[float], y: Array_1[float]) -> ValueTuple_3[float, float, float]:...

    # Skipped GetNearestIndex due to it being static, abstract and generic.

    GetNearestIndex : GetNearestIndex_MethodGroup
    class GetNearestIndex_MethodGroup:
        @typing.overload
        def __call__(self, x: Array_1[float], xValue: float, ascending: bool) -> int:...
        @typing.overload
        def __call__(self, xValues: Array_1[float], yValues: Array_1[float], x: float, y: float, iStart: int, iEnd: int) -> int:...
        @typing.overload
        def __call__(self, c: Curve, x: float, y: float, iStart: int, iEnd: int, normalize: bool = ...) -> int:...

    # Skipped Gradient due to it being static, abstract and generic.

    Gradient : Gradient_MethodGroup
    class Gradient_MethodGroup:
        @typing.overload
        def __call__(self, dx: float, y: Array_1[float]) -> Array_1[float]:...
        # Method Gradient(dx : Int32, y : Int32[]) was skipped since it collides with above method
        @typing.overload
        def __call__(self, x: Array_1[float], y: Array_1[float]) -> Array_1[float]:...

    # Skipped Integrate due to it being static, abstract and generic.

    Integrate : Integrate_MethodGroup
    class Integrate_MethodGroup:
        @typing.overload
        def __call__(self, c: Curve) -> float:...
        @typing.overload
        def __call__(self, c: Curve, iStart: int, iEnd: int) -> float:...
        @typing.overload
        def __call__(self, x: Array_1[float], y: Array_1[float], iStart: int, iEnd: int) -> float:...

    # Skipped Max due to it being static, abstract and generic.

    Max : Max_MethodGroup
    class Max_MethodGroup:
        @typing.overload
        def __call__(self, x: Array_1[float]) -> float:...
        # Method Max(x : Int32[]) was skipped since it collides with above method
        @typing.overload
        def __call__(self, x: Array_1[float], index: clr.Reference[int]) -> float:...
        # Method Max(x : Int32[], index : Int32&) was skipped since it collides with above method

    # Skipped MaxBy due to it being static, abstract and generic.

    MaxBy : MaxBy_MethodGroup
    class MaxBy_MethodGroup:
        def __getitem__(self, t:typing.Tuple[typing.Type[MaxBy_2_T1], typing.Type[MaxBy_2_T2]]) -> MaxBy_2[MaxBy_2_T1, MaxBy_2_T2]: ...

        MaxBy_2_T1 = typing.TypeVar('MaxBy_2_T1')
        MaxBy_2_T2 = typing.TypeVar('MaxBy_2_T2')
        class MaxBy_2(typing.Generic[MaxBy_2_T1, MaxBy_2_T2]):
            MaxBy_2_T = MathFunctions.MaxBy_MethodGroup.MaxBy_2_T1
            MaxBy_2_U = MathFunctions.MaxBy_MethodGroup.MaxBy_2_T2
            def __call__(self, source: List_1[MaxBy_2_T], key: Func_2[MaxBy_2_T, MaxBy_2_U]) -> MaxBy_2_T:...


    # Skipped Min due to it being static, abstract and generic.

    Min : Min_MethodGroup
    class Min_MethodGroup:
        @typing.overload
        def __call__(self, x: Array_1[float]) -> float:...
        @typing.overload
        def __call__(self, x: Array_1[float], index: clr.Reference[int]) -> float:...

    # Skipped MinBy due to it being static, abstract and generic.

    MinBy : MinBy_MethodGroup
    class MinBy_MethodGroup:
        def __getitem__(self, t:typing.Tuple[typing.Type[MinBy_2_T1], typing.Type[MinBy_2_T2]]) -> MinBy_2[MinBy_2_T1, MinBy_2_T2]: ...

        MinBy_2_T1 = typing.TypeVar('MinBy_2_T1')
        MinBy_2_T2 = typing.TypeVar('MinBy_2_T2')
        class MinBy_2(typing.Generic[MinBy_2_T1, MinBy_2_T2]):
            MinBy_2_T = MathFunctions.MinBy_MethodGroup.MinBy_2_T1
            MinBy_2_U = MathFunctions.MinBy_MethodGroup.MinBy_2_T2
            def __call__(self, source: List_1[MinBy_2_T], key: Func_2[MinBy_2_T, MinBy_2_U]) -> MinBy_2_T:...


    # Skipped MovingAverage due to it being static, abstract and generic.

    MovingAverage : MovingAverage_MethodGroup
    class MovingAverage_MethodGroup:
        def __call__(self, y: Array_1[float], windowSize: int) -> Array_1[float]:...
        # Method MovingAverage(y : Int32[], windowSize : Int32) was skipped since it collides with above method

    # Skipped SD due to it being static, abstract and generic.

    SD : SD_MethodGroup
    class SD_MethodGroup:
        @typing.overload
        def __call__(self, y: Array_1[float]) -> float:...
        # Method SD(y : Int32[]) was skipped since it collides with above method
        @typing.overload
        def __call__(self, index: int, count: int, y: Array_1[float]) -> float:...
        # Method SD(index : Int32, count : Int32, y : Int32[]) was skipped since it collides with above method



class MatrixObj_GenericClasses(abc.ABCMeta):
    Generic_MatrixObj_GenericClasses_MatrixObj_1_T = typing.TypeVar('Generic_MatrixObj_GenericClasses_MatrixObj_1_T', bound=Union[IEquatable_1[MatrixObj_GenericClasses_MatrixObj_1_T], IFormattable])
    def __getitem__(self, types : typing.Type[Generic_MatrixObj_GenericClasses_MatrixObj_1_T]) -> typing.Type[MatrixObj_1[Generic_MatrixObj_GenericClasses_MatrixObj_1_T]]: ...

MatrixObj : MatrixObj_GenericClasses

MatrixObj_1_T = typing.TypeVar('MatrixObj_1_T', bound=Union[IEquatable_1[MatrixObj_1_T], IFormattable])
class MatrixObj_1(typing.Generic[MatrixObj_1_T], IEquatable_1[MatrixObj_1[MatrixObj_1_T]], abc.ABC):
    NColumns : int
    NRows : int
    TypeOf : typing.Type[typing.Any]
    @property
    def Item(self) -> MatrixObj_1_T: ...
    @Item.setter
    def Item(self, value: MatrixObj_1_T) -> MatrixObj_1_T: ...
    def AppendToBottom(self, bottom: MatrixObj_1[MatrixObj_1_T]) -> MatrixObj_1[MatrixObj_1_T]: ...
    def AppendToRight(self, right: MatrixObj_1[MatrixObj_1_T]) -> MatrixObj_1[MatrixObj_1_T]: ...
    def Equals(self, other: MatrixObj_1[MatrixObj_1_T]) -> bool: ...
    @abc.abstractmethod
    def SubMatrix(self, sourceRowIndex: int, rowCount: int, sourceColumnIndex: int, columnCount: int) -> MatrixObj_1[MatrixObj_1_T]: ...
    # Skipped At due to it being static, abstract and generic.

    At : At_MethodGroup[MatrixObj_1_T]
    At_MethodGroup_MatrixObj_1_T = typing.TypeVar('At_MethodGroup_MatrixObj_1_T', bound=Union[IEquatable_1[At_MethodGroup_MatrixObj_1_T], IFormattable])
    class At_MethodGroup(typing.Generic[At_MethodGroup_MatrixObj_1_T]):
        At_MethodGroup_MatrixObj_1_T = MatrixObj_1.At_MethodGroup_MatrixObj_1_T
        @typing.overload
        def __call__(self, row: int, column: int) -> At_MethodGroup_MatrixObj_1_T:...
        @typing.overload
        def __call__(self, row: int, column: int, value: At_MethodGroup_MatrixObj_1_T) -> None:...

    # Skipped CopyTo due to it being static, abstract and generic.

    CopyTo : CopyTo_MethodGroup[MatrixObj_1_T]
    CopyTo_MethodGroup_MatrixObj_1_T = typing.TypeVar('CopyTo_MethodGroup_MatrixObj_1_T', bound=Union[IEquatable_1[CopyTo_MethodGroup_MatrixObj_1_T], IFormattable])
    class CopyTo_MethodGroup(typing.Generic[CopyTo_MethodGroup_MatrixObj_1_T]):
        CopyTo_MethodGroup_MatrixObj_1_T = MatrixObj_1.CopyTo_MethodGroup_MatrixObj_1_T
        @typing.overload
        def __call__(self, target: MatrixObj_1[CopyTo_MethodGroup_MatrixObj_1_T]) -> None:...
        @typing.overload
        def __call__(self, target: MatrixObj_1[CopyTo_MethodGroup_MatrixObj_1_T], sourceRowIndex: int, targetRowIndex: int, rowCount: int, sourceColumnIndex: int, targetColumnIndex: int, columnCount: int) -> None:...



class PolyCurve:
    def __init__(self, sourceCurve: Curve) -> None: ...
    CurveGenerated : Curve
    GlobalO : int
    Indices : Dictionary_2[PointF, int]
    Points : List_1[PointF]
    @property
    def EndIndex(self) -> int: ...
    @property
    def GetClosestPoint(self) -> PointF: ...
    @property
    def GetFarestPoint(self) -> PointF: ...
    @property
    def StartIndex(self) -> int: ...
    @staticmethod
    def RegVal(x: float, C: Array_1[float], O: int) -> float: ...
    # Skipped AddPoint due to it being static, abstract and generic.

    AddPoint : AddPoint_MethodGroup
    class AddPoint_MethodGroup:
        @typing.overload
        def __call__(self, newX: float, newY: float) -> None:...
        @typing.overload
        def __call__(self, newX: float, newY: float, iOrgCurve: int) -> None:...

    # Skipped GetPolyCurve due to it being static, abstract and generic.

    GetPolyCurve : GetPolyCurve_MethodGroup
    class GetPolyCurve_MethodGroup:
        @typing.overload
        def __call__(self, sourceXArray: DataArray) -> Curve:...
        @typing.overload
        def __call__(self, x1: float, x2: float) -> Curve:...
        @typing.overload
        def __call__(self, x1: float, x2: float, nPoints: float) -> Curve:...



class SortPoints(abc.ABC):
    @staticmethod
    def SortPointsArray(pArray: Array_1[PointF]) -> Array_1[PointF]: ...


class SparseMatrix_GenericClasses(abc.ABCMeta):
    Generic_SparseMatrix_GenericClasses_SparseMatrix_1_T = typing.TypeVar('Generic_SparseMatrix_GenericClasses_SparseMatrix_1_T', bound=Union[IEquatable_1[SparseMatrix_GenericClasses_SparseMatrix_1_T], IFormattable])
    def __getitem__(self, types : typing.Type[Generic_SparseMatrix_GenericClasses_SparseMatrix_1_T]) -> typing.Type[SparseMatrix_1[Generic_SparseMatrix_GenericClasses_SparseMatrix_1_T]]: ...

SparseMatrix : SparseMatrix_GenericClasses

SparseMatrix_1_T = typing.TypeVar('SparseMatrix_1_T', bound=Union[IEquatable_1[SparseMatrix_1_T], IFormattable])
class SparseMatrix_1(typing.Generic[SparseMatrix_1_T], MatrixObj_1[SparseMatrix_1_T]):
    def __init__(self, nRows: int, nColumns: int) -> None: ...
    ColumnIndices : Array_1[int]
    NColumns : int
    NRows : int
    RowPointers : Array_1[int]
    TypeOf : typing.Type[typing.Any]
    Values : Array_1[SparseMatrix_1_T]
    Zero : SparseMatrix_1_T
    @property
    def Item(self) -> SparseMatrix_1_T: ...
    @Item.setter
    def Item(self, value: SparseMatrix_1_T) -> SparseMatrix_1_T: ...
    @property
    def ValueCount(self) -> int: ...
    def FindItem(self, row: int, column: int) -> int: ...
    def SubMatrix(self, sourceRowIndex: int, rowCount: int, sourceColumnIndex: int, columnCount: int) -> MatrixObj_1[SparseMatrix_1_T]: ...
    # Skipped At due to it being static, abstract and generic.

    At : At_MethodGroup[SparseMatrix_1_T]
    At_MethodGroup_SparseMatrix_1_T = typing.TypeVar('At_MethodGroup_SparseMatrix_1_T', bound=Union[IEquatable_1[At_MethodGroup_SparseMatrix_1_T], IFormattable])
    class At_MethodGroup(typing.Generic[At_MethodGroup_SparseMatrix_1_T]):
        At_MethodGroup_SparseMatrix_1_T = SparseMatrix_1.At_MethodGroup_SparseMatrix_1_T
        @typing.overload
        def __call__(self, row: int, column: int) -> At_MethodGroup_SparseMatrix_1_T:...
        @typing.overload
        def __call__(self, row: int, column: int, value: At_MethodGroup_SparseMatrix_1_T) -> None:...
