"""Submodule for measurement references and data.

[MeasurementRef][] references a stored measurement, [MeasurementJob][]
represents an ongoing measurement, and [Measurement][] holds the complete
data of a finished measurement.

"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Self, overload, override

import System

from .._data import Method
from .._types import MethodTypeCompatible
from ._data import Dataset
from .models._wire import MeasurementListResult, MeasurementResult

if TYPE_CHECKING:
    from ._session import Session


class MeasurementRef:
    """
    A reference to a measurement.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_guid', '_metadata', '_session')
    _guid: str  # pyright: ignore[reportUninitializedInstanceVariable]
    _metadata: MeasurementListResult  # pyright: ignore[reportUninitializedInstanceVariable]
    _session: Session  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'MeasurementRef cannot be instantiated directly. '
            'Obtain instances through Session.list_measurements(). '
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(guid={self.guid!r})'

    @classmethod
    def _wrap(cls, metadata: MeasurementListResult, session: Session) -> Self:
        obj = object.__new__(cls)
        obj._guid = str(metadata.Id)
        obj._metadata = metadata
        obj._session = session
        return obj

    @property
    def guid(self) -> str:
        """The unique identifier of the measurement."""
        return self._guid

    async def fetch_metadata(self) -> MeasurementListResult:
        await self._session.fetch_measurement_metadata()

    async def fetch(self) -> Measurement:
        """Fetch data for this measurement."""
        return await self._session.fetch_measurement(self)


class MeasurementJob:
    """
    A job representing an ongoing measurement.
    """

    def __init__(self, guid: str, serial: str):
        self._guid: str = guid
        self._serial: str = serial

    def __repr__(self):
        return f'{type(self).__name__}(guid={self.guid!r}, serial={self.serial_number!r})'

    @property
    def guid(self):
        """The unique identifier of the measurement being performed."""
        return self._guid

    @property
    def serial_number(self):
        """Serial number of the instrument carrying out the measurement."""
        return self._serial

    @classmethod
    def from_response(cls, response: dict[str, Any]):
        if error := response.get('exceptionMessage'):
            raise ConnectionError(error['resourceKey'])

        return cls(guid=response['result'], serial=response['serial'])

    @property
    def is_finished(self) -> bool:
        """True if the measurement is finished."""
        raise NotImplementedError

    async def cancel(self) -> None:
        """Cancel running measurement."""
        raise NotImplementedError

    async def result(self) -> MeasurementRef:
        """Wait for the measurement to finish and return measurement reference.

        Returns
        -------
        MeasurementRef
            Reference to the measurement data.
        """
        return MeasurementRef(self.guid)

    def __await__(self):
        return self.result().__await__()


class Measurement(Sequence[Dataset]):
    """
    Measurement data containing multiple datasets.

    """

    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSData.LablinkMeasurement  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Measurement cannot be instantiated directly. '
            'Obtain instances through Session.fetch_measurement() or MeasurementJob.result().'
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name='{self._inner.Method.Name}', timestamp='{self.timestamp}')"

    @classmethod
    def _wrap(cls, inner: MeasurementResult) -> Self:
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
        """The datasets contained in this measurement."""
        return [Dataset._wrap(obj) for obj in self._inner]

    @property
    def guid(self) -> str:
        """The unique identifier of the measurement."""
        return str(self._inner.Id)

    @property
    def serial_number(self) -> str:
        """The serial number of the instrument used for the measurement."""
        return self._inner.InstrumentSerial

    @property
    def method(self) -> MethodTypeCompatible:
        """The method settings used for this measurement."""
        return Method._wrap(self._inner.Method).to_settings()

    @property
    def timestamp(self) -> datetime:
        """The UTC date and time when the measurement was recorded."""
        timestamp = self._inner.UtcDateTime
        return datetime.fromisoformat(
            timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)
        )

    @property
    def is_read_only(self) -> bool:
        """Whether the measurement data is read-only."""
        return self._inner.IsReadOnly

    @property
    def is_finished(self) -> bool:
        """Whether the measurement has finished."""
        return self._inner.IsFinished
