from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ClassVar, Literal, Self, overload, override

import System
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Dtos as PSDtos

from pypalmsens._converters import single_to_double
from pypalmsens._data.data_array import implementation
from pypalmsens._types import AllowedCurrentRanges, AllowedReadingStatus, AllowedTimingStatus

AllowedDataValueTypes = Literal[
    'Index',
    'CycleIndex',
    'LevelIndex',
    'Timestamp',
    'Frequency',
    'TimingStatus',
    'AppliedCurrent',
    'MeasuredCurrent',
    'ForwardCurrent',
    'ReverseCurrent',
    'ACCurrent',
    'DCCurrent',
    'CurrentRange',
    'CurrentReadingStatus',
    'ForwardCurrentReadingStatus',
    'ReverseCurrentReadingStatus',
    'MeasuredWE2Current',
    'ForwardWE2Current',
    'ReverseWE2Current',
    'ACWE2Current',
    'DCWE2Current',
    'WE2CurrentRange',
    'WE2CurrentReadingStatus',
    'ForwardWE2CurrentReadingStatus',
    'ReverseWE2CurrentReadingStatus',
    'AppliedPotential',
    'AppliedWE2Potential',
    'MeasuredPotential',
    'MeasuredWECEPotential',
    'ACPotential',
    'DCPotential',
    'ACWECEPotential',
    'DCWECEPotential',
    'ACRECEPotential',
    'DCRECEPotential',
    'PotentialRange',
    'PotentialReadingStatus',
    'AuxiliaryPotential',
    'Charge',
    'ImpedanceReal',
    'ImpedanceImaginary',
    'ImpedanceMagnitude',
    'ImpedancePhase',
    'AdmittanceReal',
    'AdmittanceImaginary',
    'AdmittanceMagnitude',
    'CapacitanceReal',
    'CapacitanceImaginary',
    'CapacitanceSeries',
    'ScpValue',
    'dEdt',
    'Temperature',
    'CustomUnit',
]


Converter = Callable[[Any], Any]

_CONVERTERS: dict[type, Converter] = {}


def _converts(value_type: type):
    """Decorator registering a converter for the DataValueType."""

    def _wrapped(fn: Converter) -> Converter:
        _CONVERTERS[value_type] = fn
        return fn

    return _wrapped


@_converts(System.TimeSpan)
def _(obj: System.TimeSpan) -> float:
    return obj.TotalSeconds


@_converts(PSDtos.TimingStatus)
def _(obj: PSDtos.TimingStatus) -> AllowedTimingStatus:
    return str(obj)


@_converts(PSData.CurrentRange)
def _(obj: PSData.CurrentRange) -> AllowedCurrentRanges:
    # Alternative: also has obj.Factor
    return obj.Value.ToString().lstrip('cr')


@_converts(PSDtos.ReadingStatus)
def _(obj: PSDtos.ReadingStatus) -> AllowedReadingStatus:
    return str(obj)


@_converts(float)
def _(obj: float) -> float:
    return single_to_double(obj)


class DataArray(Sequence[Any]):
    __slots__: ClassVar[tuple[str, ...]] = (
        '_converter',
        '_inner',
    )
    _inner: PSData.LablinkArray  # pyright: ignore[reportUninitializedInstanceVariable]
    _converter: Converter  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Dataset cannot be instantiated directly. Obtain instances through other classes.'
        )

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}(name={self.name}, unit={self.unit}, n_points={len(self)})'
        )

    def _resolve_converter(self) -> Converter:
        value_type = type(self._inner[0]) if len(self) else None
        if value_type is None:
            return lambda x: x
        for cls in type.mro(value_type):
            if cls in _CONVERTERS:
                return _CONVERTERS[cls]
        return lambda x: x

    @classmethod
    def _wrap(cls, inner: PSData.LablinkArray) -> Self:
        obj = cls.__new__(cls)
        obj._inner = implementation(inner)
        obj._converter = obj._resolve_converter()
        return obj

    def __len__(self) -> int:
        return self._inner.Count

    @overload
    def __getitem__(self, index: int) -> Any: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Any]: ...

    @override
    def __getitem__(self, index):
        length = len(self)
        if isinstance(index, slice):
            return [self._converter(v) for v in self._inner[index]]
        if not isinstance(index, int):
            raise TypeError(f'indices must be integers, not {type(index).__name__}')
        if index >= length or index < -length:
            raise IndexError('list index out of range')

        return self._converter(self._inner[index % length])

    @property
    def name(self) -> str:
        return self.type

    @property
    def type(self) -> AllowedDataValueTypes:
        return str(self._inner.DataValueType)  # type: ignore

    @property
    def unit(self) -> str:
        return self._inner.Unit


class Dataset(Sequence[DataArray]):
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSData.LablinkDataSet  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Dataset cannot be instantiated directly. Obtain instances through other classes.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.array_types()})'

    @classmethod
    def _wrap(cls, inner: PSData.LablinkDataSet) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @override
    def __len__(self):
        return self._inner.Count

    @overload
    def __getitem__(self, index: int) -> DataArray: ...

    @overload
    def __getitem__(self, index: slice) -> list[DataArray]: ...

    @override
    def __getitem__(self, index) -> DataArray | list[DataArray]:
        if isinstance(index, int):
            if index >= len(self) or index < -len(self):
                raise IndexError('list index out of range')
            index = index % len(self)
            return DataArray._wrap(self._inner[index])

        if isinstance(index, slice):
            raise NotImplementedError

    def array_types(self) -> list[str]:
        return [array.type for array in self.arrays()]

    def arrays(self) -> list[DataArray]:
        return [DataArray._wrap(obj) for obj in self._inner]
