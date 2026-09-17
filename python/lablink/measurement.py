from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any, ClassVar, Self, overload, override

import System
from PalmSens import Method as PSMethod
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Dtos as PSDtos

from pypalmsens._converters import single_to_double
from pypalmsens._data import Method
from pypalmsens._data.data_array import implementation
from pypalmsens._types import AllowedCurrentRanges, AllowedReadingStatus, AllowedTimingStatus
from pypalmsens.types import AllowedMethods, MethodTypeCompatible


class MeasurementInfo:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSData.MeasurementInfo  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'InstrumentInfo cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name}, guid={self.guid})'

    @classmethod
    def _wrap(cls, inner: PSData.MeasurementInfo) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def timestamp(self) -> datetime:
        """Date and time at which this measurement was created.

        Returns a timezone-naive `datetime` in local time, matching the format
        used by the SDK (e.g. ``2017-07-12 14:28:58``).
        """
        timestamp = self._inner.CreatedOn
        return datetime.fromisoformat(
            timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)
        )

    @property
    def guid(self) -> str:
        return str(self._inner.Id)

    @property
    def name(self) -> str:
        return self._inner.Name

    @property
    def n_points(self) -> int:
        """Number of points in this measurement."""
        return self._inner.Points

    def method_id(self) -> AllowedMethods:
        return PSMethod.FromTechniqueNumber(int(self._inner.Technique)).MethodID

    def user(self) -> str | None:
        return self._inner.User


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
    def type(self) -> str:
        return str(self._inner.DataValueType)

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
        return f'{type(self).__name__}(...)'

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
    def __getitem__(self, index: slice) -> Sequence[DataArray]: ...

    @override
    def __getitem__(self, index):
        if isinstance(index, int):
            if index >= len(self) or index < -len(self):
                raise IndexError('list index out of range')
            index = index % len(self)
            return DataArray._wrap(self._inner[index])

        if isinstance(index, slice):
            raise NotImplementedError

    def arrays(self) -> list[DataArray]:
        return [DataArray._wrap(obj) for obj in self._inner]


class Measurement(Sequence[Dataset]):
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSData.LablinkMeasurement  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'LablinkMeasurement cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name='{self._inner.Method.Name}', timestamp='{self.timestamp}')"

    @classmethod
    def _wrap(cls, inner: PSData.LablinkMeasurement) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @override
    def __len__(self):
        return self._inner.Count

    @overload
    def __getitem__(self, index: int) -> Dataset: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Dataset]: ...

    @override
    def __getitem__(self, index):
        if isinstance(index, int):
            if index >= len(self) or index < -len(self):
                raise IndexError('list index out of range')
            index = index % len(self)
            return Dataset._wrap(self._inner[index])

        if isinstance(index, slice):
            raise NotImplementedError

    @property
    def datasets(self) -> list[Dataset]:
        return [Dataset._wrap(obj) for obj in self._inner]

    @property
    def guid(self) -> str:
        return str(self._inner.Id)

    @property
    def serial_number(self) -> str:
        return self._inner.InstrumentSerial

    @property
    def method(self) -> MethodTypeCompatible:
        return Method._wrap(self._inner.Method).to_settings()

    @property
    def timestamp(self) -> datetime:
        timestamp = self._inner.UtcDateTime
        return datetime.fromisoformat(
            timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)
        )

    @property
    def is_read_only(self) -> bool:
        return self._inner.IsReadOnly

    @property
    def is_finished(self) -> bool:
        return self._inner.IsFinished
