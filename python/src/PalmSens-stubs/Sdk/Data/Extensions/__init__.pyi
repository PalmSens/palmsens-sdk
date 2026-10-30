import typing, abc
from System.Threading.Tasks import Task
from System.Collections.Generic import IEnumerable_1, IReadOnlyList_1, IDictionary_2, List_1, IAsyncEnumerable_1, IList_1, IComparer_1
from System import Func_2, ValueTuple_2, Func_1, TimeSpan
from System.Threading import CancellationToken
from System.Numerics import IAdditiveIdentity_2, IAdditionOperators_3
from System.Collections.ObjectModel import ObservableCollection_1

class CollectionExtensions(abc.ABC):
    @staticmethod
    def AggregateExceptions(callbacks: IEnumerable_1[Func_2[CancellationToken, Task]], cancellationToken: CancellationToken = ...) -> Task: ...
    @staticmethod
    def HasBit(bytes: IReadOnlyList_1[int], bitIndex: int) -> bool: ...
    # Skipped AddToListOrCreateNew due to it being static, abstract and generic.

    AddToListOrCreateNew : AddToListOrCreateNew_MethodGroup
    class AddToListOrCreateNew_MethodGroup:
        def __getitem__(self, t:typing.Tuple[typing.Type[AddToListOrCreateNew_2_T1], typing.Type[AddToListOrCreateNew_2_T2]]) -> AddToListOrCreateNew_2[AddToListOrCreateNew_2_T1, AddToListOrCreateNew_2_T2]: ...

        AddToListOrCreateNew_2_T1 = typing.TypeVar('AddToListOrCreateNew_2_T1')
        AddToListOrCreateNew_2_T2 = typing.TypeVar('AddToListOrCreateNew_2_T2')
        class AddToListOrCreateNew_2(typing.Generic[AddToListOrCreateNew_2_T1, AddToListOrCreateNew_2_T2]):
            AddToListOrCreateNew_2_TKey = CollectionExtensions.AddToListOrCreateNew_MethodGroup.AddToListOrCreateNew_2_T1
            AddToListOrCreateNew_2_TValue = CollectionExtensions.AddToListOrCreateNew_MethodGroup.AddToListOrCreateNew_2_T2
            def __call__(self, dictionary: IDictionary_2[AddToListOrCreateNew_2_TKey, List_1[AddToListOrCreateNew_2_TValue]], key: AddToListOrCreateNew_2_TKey, value: AddToListOrCreateNew_2_TValue) -> None:...


    # Skipped ConditionallyAppend due to it being static, abstract and generic.

    ConditionallyAppend : ConditionallyAppend_MethodGroup
    class ConditionallyAppend_MethodGroup:
        def __getitem__(self, t:typing.Type[ConditionallyAppend_1_T1]) -> ConditionallyAppend_1[ConditionallyAppend_1_T1]: ...

        ConditionallyAppend_1_T1 = typing.TypeVar('ConditionallyAppend_1_T1')
        class ConditionallyAppend_1(typing.Generic[ConditionallyAppend_1_T1]):
            ConditionallyAppend_1_T = CollectionExtensions.ConditionallyAppend_MethodGroup.ConditionallyAppend_1_T1
            def __call__(self, enumerable: IEnumerable_1[ConditionallyAppend_1_T], predicate: bool, value: ConditionallyAppend_1_T) -> IEnumerable_1[ConditionallyAppend_1_T]:...


    # Skipped Enumerate due to it being static, abstract and generic.

    Enumerate : Enumerate_MethodGroup
    class Enumerate_MethodGroup:
        def __getitem__(self, t:typing.Type[Enumerate_1_T1]) -> Enumerate_1[Enumerate_1_T1]: ...

        Enumerate_1_T1 = typing.TypeVar('Enumerate_1_T1')
        class Enumerate_1(typing.Generic[Enumerate_1_T1]):
            Enumerate_1_T = CollectionExtensions.Enumerate_MethodGroup.Enumerate_1_T1
            @typing.overload
            def __call__(self, collection: IEnumerable_1[Enumerate_1_T]) -> IEnumerable_1[ValueTuple_2[Enumerate_1_T, int]]:...
            @typing.overload
            def __call__(self, collection: IAsyncEnumerable_1[Enumerate_1_T]) -> IAsyncEnumerable_1[ValueTuple_2[Enumerate_1_T, int]]:...


    # Skipped GetOrCreate due to it being static, abstract and generic.

    GetOrCreate : GetOrCreate_MethodGroup
    class GetOrCreate_MethodGroup:
        def __getitem__(self, t:typing.Tuple[typing.Type[GetOrCreate_2_T1], typing.Type[GetOrCreate_2_T2]]) -> GetOrCreate_2[GetOrCreate_2_T1, GetOrCreate_2_T2]: ...

        GetOrCreate_2_T1 = typing.TypeVar('GetOrCreate_2_T1')
        GetOrCreate_2_T2 = typing.TypeVar('GetOrCreate_2_T2')
        class GetOrCreate_2(typing.Generic[GetOrCreate_2_T1, GetOrCreate_2_T2]):
            GetOrCreate_2_TKey = CollectionExtensions.GetOrCreate_MethodGroup.GetOrCreate_2_T1
            GetOrCreate_2_TValue = CollectionExtensions.GetOrCreate_MethodGroup.GetOrCreate_2_T2
            @typing.overload
            def __call__(self, dictionary: IDictionary_2[GetOrCreate_2_TKey, GetOrCreate_2_TValue], key: GetOrCreate_2_TKey) -> GetOrCreate_2_TValue:...
            @typing.overload
            def __call__(self, dictionary: IDictionary_2[GetOrCreate_2_TKey, GetOrCreate_2_TValue], key: GetOrCreate_2_TKey, valueConstructor: Func_1[GetOrCreate_2_TValue]) -> GetOrCreate_2_TValue:...


    # Skipped IndexOf due to it being static, abstract and generic.

    IndexOf : IndexOf_MethodGroup
    class IndexOf_MethodGroup:
        def __getitem__(self, t:typing.Type[IndexOf_1_T1]) -> IndexOf_1[IndexOf_1_T1]: ...

        IndexOf_1_T1 = typing.TypeVar('IndexOf_1_T1')
        class IndexOf_1(typing.Generic[IndexOf_1_T1]):
            IndexOf_1_T = CollectionExtensions.IndexOf_MethodGroup.IndexOf_1_T1
            @typing.overload
            def __call__(self, list: IReadOnlyList_1[IndexOf_1_T], predicate: Func_2[IndexOf_1_T, bool]) -> int:...
            @typing.overload
            def __call__(self, list: IReadOnlyList_1[IndexOf_1_T], value: IndexOf_1_T) -> int:...


    # Skipped InsertSorted due to it being static, abstract and generic.

    InsertSorted : InsertSorted_MethodGroup
    class InsertSorted_MethodGroup:
        def __getitem__(self, t:typing.Type[InsertSorted_1_T1]) -> InsertSorted_1[InsertSorted_1_T1]: ...

        InsertSorted_1_T1 = typing.TypeVar('InsertSorted_1_T1')
        class InsertSorted_1(typing.Generic[InsertSorted_1_T1]):
            InsertSorted_1_T = CollectionExtensions.InsertSorted_MethodGroup.InsertSorted_1_T1
            @typing.overload
            def __call__(self, list: IList_1[InsertSorted_1_T], items: IEnumerable_1[InsertSorted_1_T]) -> None:...
            @typing.overload
            def __call__(self, list: IList_1[InsertSorted_1_T], item: InsertSorted_1_T) -> int:...
            @typing.overload
            def __call__(self, list: IList_1[InsertSorted_1_T], items: IEnumerable_1[InsertSorted_1_T], comparer: IComparer_1[InsertSorted_1_T]) -> None:...
            @typing.overload
            def __call__(self, list: IList_1[InsertSorted_1_T], item: InsertSorted_1_T, comparer: IComparer_1[InsertSorted_1_T]) -> int:...


    # Skipped IntersectMany due to it being static, abstract and generic.

    IntersectMany : IntersectMany_MethodGroup
    class IntersectMany_MethodGroup:
        def __getitem__(self, t:typing.Tuple[typing.Type[IntersectMany_2_T1], typing.Type[IntersectMany_2_T2]]) -> IntersectMany_2[IntersectMany_2_T1, IntersectMany_2_T2]: ...

        IntersectMany_2_T1 = typing.TypeVar('IntersectMany_2_T1')
        IntersectMany_2_T2 = typing.TypeVar('IntersectMany_2_T2')
        class IntersectMany_2(typing.Generic[IntersectMany_2_T1, IntersectMany_2_T2]):
            IntersectMany_2_TSource = CollectionExtensions.IntersectMany_MethodGroup.IntersectMany_2_T1
            IntersectMany_2_TResult = CollectionExtensions.IntersectMany_MethodGroup.IntersectMany_2_T2
            def __call__(self, source: IEnumerable_1[IntersectMany_2_TSource], func: Func_2[IntersectMany_2_TSource, IEnumerable_1[IntersectMany_2_TResult]]) -> IEnumerable_1[IntersectMany_2_TResult]:...


    # Skipped KeySetEquals due to it being static, abstract and generic.

    KeySetEquals : KeySetEquals_MethodGroup
    class KeySetEquals_MethodGroup:
        def __getitem__(self, t:typing.Tuple[typing.Type[KeySetEquals_3_T1], typing.Type[KeySetEquals_3_T2], typing.Type[KeySetEquals_3_T3]]) -> KeySetEquals_3[KeySetEquals_3_T1, KeySetEquals_3_T2, KeySetEquals_3_T3]: ...

        KeySetEquals_3_T1 = typing.TypeVar('KeySetEquals_3_T1')
        KeySetEquals_3_T2 = typing.TypeVar('KeySetEquals_3_T2')
        KeySetEquals_3_T3 = typing.TypeVar('KeySetEquals_3_T3')
        class KeySetEquals_3(typing.Generic[KeySetEquals_3_T1, KeySetEquals_3_T2, KeySetEquals_3_T3]):
            KeySetEquals_3_TKey = CollectionExtensions.KeySetEquals_MethodGroup.KeySetEquals_3_T1
            KeySetEquals_3_TVal1 = CollectionExtensions.KeySetEquals_MethodGroup.KeySetEquals_3_T2
            KeySetEquals_3_TVal2 = CollectionExtensions.KeySetEquals_MethodGroup.KeySetEquals_3_T3
            def __call__(self, dict1: IDictionary_2[KeySetEquals_3_TKey, KeySetEquals_3_TVal1], dict2: IDictionary_2[KeySetEquals_3_TKey, KeySetEquals_3_TVal2]) -> bool:...


    # Skipped PopBack due to it being static, abstract and generic.

    PopBack : PopBack_MethodGroup
    class PopBack_MethodGroup:
        def __getitem__(self, t:typing.Type[PopBack_1_T1]) -> PopBack_1[PopBack_1_T1]: ...

        PopBack_1_T1 = typing.TypeVar('PopBack_1_T1')
        class PopBack_1(typing.Generic[PopBack_1_T1]):
            PopBack_1_T = CollectionExtensions.PopBack_MethodGroup.PopBack_1_T1
            def __call__(self, list: IList_1[PopBack_1_T], count: int = ...) -> None:...


    # Skipped RemoveAll due to it being static, abstract and generic.

    RemoveAll : RemoveAll_MethodGroup
    class RemoveAll_MethodGroup:
        def __getitem__(self, t:typing.Type[RemoveAll_1_T1]) -> RemoveAll_1[RemoveAll_1_T1]: ...

        RemoveAll_1_T1 = typing.TypeVar('RemoveAll_1_T1')
        class RemoveAll_1(typing.Generic[RemoveAll_1_T1]):
            RemoveAll_1_T = CollectionExtensions.RemoveAll_MethodGroup.RemoveAll_1_T1
            def __call__(self, list: IList_1[RemoveAll_1_T], predicate: Func_2[RemoveAll_1_T, bool]) -> int:...


    # Skipped Sum due to it being static, abstract and generic.

    Sum : Sum_MethodGroup
    class Sum_MethodGroup:
        @typing.overload
        def __getitem__(self, t:typing.Type[Sum_1_T1]) -> Sum_1[Sum_1_T1]: ...

        Sum_1_T1 = typing.TypeVar('Sum_1_T1')
        class Sum_1(typing.Generic[Sum_1_T1]):
            Sum_1_TSource = CollectionExtensions.Sum_MethodGroup.Sum_1_T1
            def __call__(self, source: IEnumerable_1[Sum_1_TSource], selector: Func_2[Sum_1_TSource, TimeSpan]) -> TimeSpan:...

        @typing.overload
        def __getitem__(self, t:typing.Tuple[typing.Type[Sum_2_T1], typing.Type[Sum_2_T2]]) -> Sum_2[Sum_2_T1, Sum_2_T2]: ...

        Sum_2_T1 = typing.TypeVar('Sum_2_T1')
        Sum_2_T2 = typing.TypeVar('Sum_2_T2', bound=Union[IAdditiveIdentity_2[Sum_2_TValue, Sum_2_TValue], IAdditionOperators_3[Sum_2_TValue, Sum_2_TValue, Sum_2_TValue]])
        class Sum_2(typing.Generic[Sum_2_T1, Sum_2_T2]):
            Sum_2_TSource = CollectionExtensions.Sum_MethodGroup.Sum_2_T1
            Sum_2_TValue = CollectionExtensions.Sum_MethodGroup.Sum_2_T2
            def __call__(self, source: IEnumerable_1[Sum_2_TSource], selector: Func_2[Sum_2_TSource, Sum_2_TValue]) -> Sum_2_TValue:...


    # Skipped ToObservableCollection due to it being static, abstract and generic.

    ToObservableCollection : ToObservableCollection_MethodGroup
    class ToObservableCollection_MethodGroup:
        def __getitem__(self, t:typing.Type[ToObservableCollection_1_T1]) -> ToObservableCollection_1[ToObservableCollection_1_T1]: ...

        ToObservableCollection_1_T1 = typing.TypeVar('ToObservableCollection_1_T1')
        class ToObservableCollection_1(typing.Generic[ToObservableCollection_1_T1]):
            ToObservableCollection_1_T = CollectionExtensions.ToObservableCollection_MethodGroup.ToObservableCollection_1_T1
            def __call__(self, items: IEnumerable_1[ToObservableCollection_1_T]) -> ObservableCollection_1[ToObservableCollection_1_T]:...


    # Skipped WhereNotNull due to it being static, abstract and generic.

    WhereNotNull : WhereNotNull_MethodGroup
    class WhereNotNull_MethodGroup:
        def __getitem__(self, t:typing.Type[WhereNotNull_1_T1]) -> WhereNotNull_1[WhereNotNull_1_T1]: ...

        WhereNotNull_1_T1 = typing.TypeVar('WhereNotNull_1_T1')
        class WhereNotNull_1(typing.Generic[WhereNotNull_1_T1]):
            WhereNotNull_1_T = CollectionExtensions.WhereNotNull_MethodGroup.WhereNotNull_1_T1
            def __call__(self, collection: IEnumerable_1[WhereNotNull_1_T]) -> IEnumerable_1[WhereNotNull_1_T]:...


    # Skipped Yield due to it being static, abstract and generic.

    Yield : Yield_MethodGroup
    class Yield_MethodGroup:
        def __getitem__(self, t:typing.Type[Yield_1_T1]) -> Yield_1[Yield_1_T1]: ...

        Yield_1_T1 = typing.TypeVar('Yield_1_T1')
        class Yield_1(typing.Generic[Yield_1_T1]):
            Yield_1_T = CollectionExtensions.Yield_MethodGroup.Yield_1_T1
            def __call__(self, obj: Yield_1_T) -> IEnumerable_1[Yield_1_T]:...




class CommonExtensions(abc.ABC):
    @staticmethod
    def ThrowIfNullOrEmpty(value: str, paramName: str = ...) -> str: ...
    # Skipped ThrowIfNull due to it being static, abstract and generic.

    ThrowIfNull : ThrowIfNull_MethodGroup
    class ThrowIfNull_MethodGroup:
        def __getitem__(self, t:typing.Type[ThrowIfNull_1_T1]) -> ThrowIfNull_1[ThrowIfNull_1_T1]: ...

        ThrowIfNull_1_T1 = typing.TypeVar('ThrowIfNull_1_T1')
        class ThrowIfNull_1(typing.Generic[ThrowIfNull_1_T1]):
            ThrowIfNull_1_T = CommonExtensions.ThrowIfNull_MethodGroup.ThrowIfNull_1_T1
            @typing.overload
            def __call__(self, value: typing.Optional[ThrowIfNull_1_T], paramName: str = ...) -> ThrowIfNull_1_T:...
            @typing.overload
            def __call__(self, value: ThrowIfNull_1_T, paramName: str = ...) -> ThrowIfNull_1_T:...




class MathExtensions(abc.ABC):
    @staticmethod
    def GetSIExponent(prefix: str) -> int: ...
    @staticmethod
    def GetSIFactor(prefix: str) -> float: ...
    @staticmethod
    def GetSIPrefix(exponent: int) -> str: ...
    @staticmethod
    def ToScientificFormatString(value: float) -> str: ...
    @staticmethod
    def ToScientificFormatStringWithExponent(value: float) -> str: ...
    @staticmethod
    def ToSIValueAndPrefixString(value: float, significantNumbers: int = ...) -> ValueTuple_2[str, str]: ...
    # Skipped ToDegrees due to it being static, abstract and generic.

    ToDegrees : ToDegrees_MethodGroup
    class ToDegrees_MethodGroup:
        def __call__(self, radians: float) -> float:...
        # Method ToDegrees(radians : Double) was skipped since it collides with above method

    # Skipped ToRadians due to it being static, abstract and generic.

    ToRadians : ToRadians_MethodGroup
    class ToRadians_MethodGroup:
        def __call__(self, degrees: float) -> float:...
        # Method ToRadians(degrees : Double) was skipped since it collides with above method

    # Skipped ToSIFormatString due to it being static, abstract and generic.

    ToSIFormatString : ToSIFormatString_MethodGroup
    class ToSIFormatString_MethodGroup:
        @typing.overload
        def __call__(self, value: int) -> str:...
        @typing.overload
        def __call__(self, value: float, significantNumbers: int = ...) -> str:...
