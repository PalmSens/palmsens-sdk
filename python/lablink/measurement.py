from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Self

import System
from PalmSens import Method as PSMethod
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData

from pypalmsens._data import Method
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


class LablinkMeasurement:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSData.LablinkMeasurement  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'LablinkMeasurement cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(...)'

    @classmethod
    def _wrap(cls, inner: PSData.LablinkMeasurement) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    def __len__(self):
        return self._inner.Count

    def guid(self) -> str:
        return self._inner.Guid

    def instrument_serial_number(self) -> str:
        return self._inner.InstrumentSerial

    def method(self) -> MethodTypeCompatible:
        return Method._wrap(self._inner.Method).to_settings()

    def timestamp(self) -> datetime:
        timestamp = self._inner.UtcDate
        return datetime.fromisoformat(
            timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)
        )

    def is_read_only(self) -> bool:
        return self._inner.IsReadOnly

    def is_finished(self) -> bool:
        return self._inner.IsFinished
