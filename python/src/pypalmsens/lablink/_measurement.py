"""Submodule for measurement references and data.

[MeasurementRef][] references a stored measurement, [MeasurementJob][]
represents an ongoing measurement, and [Measurement][] holds the complete
data of a finished measurement.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Self

import xarray as xr

# from ._data import Dataset
from .models._wire import MeasurementListResult

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

    def __init__(self, guid: str):
        self._guid = guid

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

    async def fetch(self) -> xr.Dataset | xr.DataTree:
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

    async def abort(self) -> None:
        raise NotImplementedError
        InstrumentClaim.abort_measurement

    async def pause(self) -> None:
        raise NotImplementedError
        InstrumentClaim.pause_measurement

    async def resume(self) -> None:
        raise NotImplementedError
        InstrumentClaim.resume_measurement
