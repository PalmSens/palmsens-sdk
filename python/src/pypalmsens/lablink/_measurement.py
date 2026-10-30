"""Submodule for measurement references and data.

[MeasurementRef][] references a stored measurement, [MeasurementJob][]
represents an ongoing measurement, and [Measurement][] holds the complete
data of a finished measurement.
"""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, ClassVar

import xarray as xr

from ._errors import NoActiveMeasurementError

if TYPE_CHECKING:
    from ._instrument import InstrumentClaim
    from ._session import Session


class Measurement:
    """
    A reference to a measurement.

    Holds the GUID of a stored measurement and an optional session link.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_guid', '_session')

    def __init__(self, guid: str, *, session: Session | None = None):
        self._guid: str = guid
        self._session: Session | None = session

    def __repr__(self) -> str:
        return f'{type(self).__name__}(guid={self.guid!r})'

    @property
    def guid(self) -> str:
        """
        The unique identifier of the measurement.

        Returns
        -------
        str
            Measurement GUID.
        """
        return self._guid

    async def get_info(self) -> None:
        """
        Get metadata for this measurement (not yet implemented).

        Raises
        ------
        RuntimeError
            If no session is attached. Reattach via
            `session.get_measurement(ref)` before calling.
        """
        if self._session is None:
            raise RuntimeError(
                f'This {type(self).__name__} is detached. Reattach it via '
                'ref = session.get_measurement(ref) before fetching data.'
            )
        raise NotImplementedError

    async def get_data(self) -> xr.Dataset | xr.DataTree:
        """
        Retrieve recorded data for this measurement.

        Returns
        -------
        xarray.Dataset or xarray.DataTree
            Measurement data. A `Dataset` is returned for a single
            measurement, a `DataTree` when the measurement contains
            repeated/stacked runs.

        Raises
        ------
        RuntimeError
            If this reference is detached from a session.
        """
        if self._session is None:
            raise RuntimeError(
                f'This {type(self).__name__} is detached. Reattach it via '
                'ref = session.get_measurement(ref) before fetching data.'
            )
        return await self._session.get_measurement(self)

    async def delete(self) -> None:
        """
        Delete this measurement from the server.

        Raises
        ------
        RuntimeError
            If this reference is detached from a session.
        """
        if self._session is None:
            raise RuntimeError(
                f'This {type(self).__name__} is detached. Reattach it via '
                '`ref = session.get_measurement(ref)` before fetching data.'
            )
        return await self._session._http.delete(f'/Measurements/{self.guid}/Delete')


class MeasurementJob:
    """
    A job representing an ongoing measurement.

    Holds the GUID of a measurement in progress and its instrument claim.
    """

    def __init__(self, guid: str, *, claim: InstrumentClaim) -> None:
        self._guid: str = guid
        self._claim: InstrumentClaim = claim
        self._is_finished: bool = False

    def __repr__(self) -> str:
        return f'{type(self).__name__}(guid={self.guid!r}, serial={self.serial_number!r})'

    @property
    def guid(self) -> str:
        """
        The unique identifier of the measurement being performed.

        Returns
        -------
        str
            Measurement GUID.
        """
        return self._guid

    @property
    def claim(self) -> InstrumentClaim:
        """The instrument claim associated with the measurement job."""
        return self._claim

    @property
    def serial_number(self) -> str:
        """Serial number of the instrument carrying out the measurement."""
        return self._claim._serial

    @property
    def is_finished(self) -> bool:
        """True if the measurement has finished."""
        return self._is_finished

    async def result(
        self,
        *,
        initial: float = 1.0,
        cap: float = 30.0,
        factor: float = 2.0,
        jitter: float = 0.15,
        timeout: float | None = None,
    ) -> Measurement:
        """
        Wait for the measurement to finish and return a reference.

        Polls `claim.get_active_measurement()` with exponential backoff so
        short jobs are caught quickly while long ones stay cheap.

        Parameters
        ----------
        initial : float, optional
            Delay before the first retry, in seconds. Defaults to 1.0.
        cap : float, optional
            Maximum delay between polls, in seconds. Defaults to 30.0.
        factor : float, optional
            Multiplier applied to the delay after each poll. Defaults to 2.0.
        jitter : float, optional
            Fractional randomness added to each delay (e.g., 0.15 for +/-15%).
            Defaults to 0.15.
        timeout : float or None, optional
            Total seconds to wait before giving up; None waits indefinitely.
            Defaults to None.

        Returns
        -------
        MeasurementRef
            A reference to the finished measurement.

        Raises
        ------
        TimeoutError
            If `timeout` is set and the measurement does not finish in time.
        """
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout if timeout else None
        delay = initial

        while True:
            await asyncio.sleep(delay * (1 + random.uniform(-jitter, jitter)))
            delay = min(delay * factor, cap)

            try:
                active = await self._claim.get_active_measurement()
            except NoActiveMeasurementError:
                break

            if not active or active.guid != self.guid:
                break

            if deadline and loop.time() >= deadline:
                raise TimeoutError(f'measurement {self.guid} did not finish in {timeout}s')

        self._is_finished = True

        return Measurement(self.guid, session=self._claim._session)

    def __await__(self):
        return self.result().__await__()

    async def abort(self) -> None:
        """Abort the measurement."""
        return await self._claim.abort_measurement()

    async def pause(self) -> None:
        """Pause the measurement."""
        return await self._claim.pause_measurement()

    async def resume(self) -> None:
        """Resume the measurement."""
        return await self._claim.resume_measurement()
