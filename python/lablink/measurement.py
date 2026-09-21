from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Self, overload, override

import System
from data import Dataset
from PalmSens import Method as PSMethod
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData

from pypalmsens._data import Method
from pypalmsens._instruments.shared import create_future
from pypalmsens.types import AllowedMethods, MethodTypeCompatible

if TYPE_CHECKING:
    from session import Session


class MeasurementRef:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner', '_session')
    _inner: PSData.MeasurementInfo  # pyright: ignore[reportUninitializedInstanceVariable]
    _session: Session  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'InstrumentInfo cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(guid={self.guid!r})'

    @classmethod
    def _wrap(cls, inner: PSData.MeasurementInfo, session: Session) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        obj._session = session
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

    async def fetch(self) -> Measurement:
        """Fetch data for this measurement."""
        return await self._session.fetch_measurement(self)


class MeasurementJob:
    def __init__(self, _net_measurement: PSData.LablinkMeasurement):
        self._inner = _net_measurement

    def __repr__(self):
        return f'{type(self).__name__}(guid={self.guid!r})'

    @property
    def guid(self):
        return str(self._inner.Id)

    async def result(self) -> Measurement:
        await create_future(self._inner.AwaitFinish)
        return Measurement._wrap(self._inner)

    def __await__(self):
        return self.result().__await__()


class Measurement(Sequence[Dataset]):
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSData.LablinkMeasurement  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Measurement cannot be instantiated directly. '
            'Obtain instances through the Session class.'
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
