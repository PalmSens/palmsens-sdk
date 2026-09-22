from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ClassVar, Literal, Self, cast, overload, override

import System
import xarray as xr
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Dtos as PSDtos

from .._data.data_array import implementation
from .._types import AllowedCurrentRanges, AllowedReadingStatus, AllowedTimingStatus

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

_CONVERTERS: dict[str, Converter] = {}


def _converts(value_types: str | list[str]):
    """Decorator registering a converter for the DataValueType."""

    def _wrapped(fn: Converter) -> Converter:
        if isinstance(value_types, str):
            value_type = value_types
            _CONVERTERS[value_type] = fn
        else:
            for value_type in value_types:
                _CONVERTERS[value_type] = fn
        return fn

    return _wrapped


@_converts(['Timestamp'])
def _(obj: System.TimeSpan) -> float:
    return obj.TotalSeconds


@_converts(['TimingStatus'])
def _(obj: PSDtos.TimingStatus) -> AllowedTimingStatus:
    return cast(AllowedTimingStatus, str(obj))


@_converts(['CurrentRange'])
def _(obj: PSData.CurrentRange) -> AllowedCurrentRanges:
    # Alternative: also has obj.Factor
    return obj.Value.ToString().lstrip('cr')


@_converts(
    ['CurrentReadingStatus', 'ForwardCurrentReadingStatus', 'ReverseCurrentReadingStatus']
)
def _(obj: PSDtos.ReadingStatus) -> AllowedReadingStatus:
    return cast(AllowedReadingStatus, str(obj))


@_converts(
    [
        'AppliedPotential',
        'Charge',
        'MeasuredCurrent',
        'AuxiliaryPotential',
        'ReverseCurrent',
        'ForwardCurrent',
    ]
)
def _(obj: float) -> float:
    return obj


@_converts(['Index', 'CycleIndex', 'LevelIndex'])
def _(obj: int) -> int:
    return obj


class DataArray(Sequence[Any]):
    __slots__: ClassVar[tuple[str, ...]] = (
        '_converter',
        '_inner',
    )
    _inner: PSData.LablinkArray
    _converter: Converter

    def __init__(self):
        raise TypeError(
            'Dataset cannot be instantiated directly. Obtain instances through other classes.'
        )

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}(name={self.name}, unit={self.unit}, n_points={len(self)})'
        )

    @classmethod
    def _wrap(cls, inner: PSData.LablinkArray) -> Self:
        obj = cls.__new__(cls)
        obj._inner = implementation(inner)
        obj._converter = _CONVERTERS[obj.type]
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
        else:
            raise NotImplementedError

    def array_types(self) -> list[str]:
        return [array.type for array in self.arrays()]

    def arrays(self) -> list[DataArray]:
        return [DataArray._wrap(obj) for obj in self._inner]

    def xarray(self) -> xr.Datase:
        arrays = list(self._inner)

        data_vars = {}
        coords = {'point': range(len(arrays[0].__implementation__))}
        attrs: dict[str, Any] = {}

        for array in arrays:
            array = array.__implementation__

            key = str(array.DataValueType)

            try:
                converter = _CONVERTERS[key]
            except KeyError:
                print(f'{key=}, \n{array.Type=}, \n{array[0]=}, \n{array=}')
                raise

            data_vars[key] = ('point', [converter(val) for val in array], {'unit': array.Unit})

        return xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
