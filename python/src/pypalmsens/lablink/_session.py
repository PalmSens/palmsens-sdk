"""Submodule for managing sessions on a Lablink instance.

Use [Session][] for an authenticated connection to a Lablink
instance. Use [ClaimBatch][] to group several instrument claims so
they can be released together.

"""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Self, overload, override

import System
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData

from .._instruments.shared import wrap_task
from ..types import MethodTypeCompatible
from ._instrument import InstrumentClaim, InstrumentRef
from ._measurement import Measurement, MeasurementJob, MeasurementRef


class ClaimBatch(Sequence[InstrumentClaim]):
    """
    A batch of instrument claims.

    Use as an async context manager. All claims are released when the
    context exits.

    Parameters
    ----------
    claims : list of InstrumentClaim
        The list of instrument claims to manage.
    """

    def __init__(self, claims: list[InstrumentClaim]):
        self.claims: list[InstrumentClaim] = claims

    @override
    def __repr__(self):
        return f'{type(self).__name__}({self.claims})'

    @overload
    def __getitem__(self, index: int) -> InstrumentClaim: ...

    @overload
    def __getitem__(self, index: slice) -> list[InstrumentClaim]: ...

    @override
    def __getitem__(self, index) -> InstrumentClaim | list[InstrumentClaim]:
        return self.claims[index]

    @override
    def __len__(self):
        return len(self.claims)

    async def __aenter__(self) -> list[InstrumentClaim]:
        return self.claims

    async def __aexit__(self, *exc_info) -> None:
        await self.release()

    async def release(self) -> None:
        """Release all instrument claims in this batch."""
        for claim in self.claims:
            await claim.release()


class Session:
    """
    A session managing a connection to a Lablink instance.

    Use [claim][] or [claim_many][] to claim instruments, and
    [start][] or [start_many][] to run measurements on them.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSLablink.Lablink  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Lablink instance cannot be instantiated directly. '
            'Obtain instances through `Instance.login()`.'
        )

    def __repr__(self) -> str:
        s = []

        if name := self.name:
            s.append(f'name={name!r}')
        s.append(f'address={self.address!r}')

        return f'{type(self).__name__}({", ".join(s)})'

    @classmethod
    def _wrap(cls, inner: PSLablink.Lablink) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def instruments(self) -> list[InstrumentRef]:
        """The instruments from the most recent [list_instruments][] call.

        May be stale or empty.
        """
        return [InstrumentRef._wrap(refs) for refs in self._inner.Instruments]

    async def list_instruments(self) -> list[InstrumentRef]:
        """List currently attached instruments.

        Refreshes the [instruments][] list.

        Returns
        -------
        list of InstrumentRef
            A list of currently attached instruments.
        """
        raise NotImplementedError('Needs PalmSens.Sdk.Lablink update')
        return [
            InstrumentRef._wrap(refs) for refs in await wrap_task(self._inner.ListInstruments())
        ]

    async def _claim(self, instruments: Sequence[InstrumentRef]) -> list[InstrumentClaim]:
        lst = System.Collections.Generic.List[PSModels.LablinkInstrumentInfo]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        refs: list[PSLablink.LablinkInstrument] = await wrap_task(
            self._inner.ConnectInstruments(lst)
        )
        return [InstrumentClaim._wrap(ref) for ref in refs]

    async def claim(self, instrument: InstrumentRef) -> InstrumentClaim:
        """Claim an instrument.

        Parameters
        ----------
        instrument : InstrumentRef
            The instrument to claim.

        Returns
        -------
        InstrumentClaim
            A claim on the instrument. Use it as an async context
            manager. It is released when the context exits.
        """
        [claim] = await self._claim([instrument])
        return claim

    async def claim_many(self, instruments: Sequence[InstrumentRef]) -> ClaimBatch:
        """Claim multiple instruments.

        Parameters
        ----------
        instruments : Sequence of InstrumentRef
            The instruments to claim.

        Returns
        -------
        ClaimBatch
            A batch containing the instrument claims.
        """
        claims = await self._claim(instruments)
        return ClaimBatch(claims)

    async def list_measurements(self) -> list[MeasurementRef]:
        """List all measurements.

        Returns
        -------
        list of MeasurementRef
            A list of measurement references.
        """
        refs: list[PSData.MeasurementInfo] = await wrap_task(self._inner.GetMeasurements())
        return [MeasurementRef._wrap(ref, self) for ref in refs]

    async def fetch_measurement(self, measurement: MeasurementRef) -> Measurement:
        """Fetch a specific measurement.

        Parameters
        ----------
        measurement : MeasurementRef
            The reference to the measurement to fetch.

        Returns
        -------
        Measurement
            The fetched measurement data.
        """
        ref: PSData.LablinkMeasurement = await wrap_task(
            self._inner.GetMeasurement(measurement._inner.Id)
        )
        return Measurement._wrap(ref)

    async def start(
        self, instrument: InstrumentClaim, *, method: MethodTypeCompatible
    ) -> MeasurementJob:
        """Start a measurement on an instrument.

        Parameters
        ----------
        instrument : InstrumentClaim
            The claimed instrument to measure.
        method : MethodTypeCompatible
            The measurement method to use.

        Returns
        -------
        MeasurementJob
            A job representing the ongoing measurement.
        """
        [measurement] = await self.start_many([instrument], method=method)
        return measurement

    async def start_many(
        self, instruments: Sequence[InstrumentClaim], *, method: MethodTypeCompatible
    ) -> list[MeasurementJob]:
        """Start measurements on multiple instruments.

        Parameters
        ----------
        instruments : Sequence of InstrumentClaim
            The claimed instruments to measure.
        method : MethodTypeCompatible
            The measurement method to use.

        Returns
        -------
        list of MeasurementJob
            A list of jobs representing the ongoing measurements.
        """
        lst = System.Collections.Generic.List[PSLablink.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        refs: list[PSData.LablinkMeasurement] = await wrap_task(
            self._inner.StartMeasurements(lst, method._to_psmethod())
        )
        return [MeasurementJob(ref) for ref in refs]

    @property
    def address(self) -> str:
        """The address of the Lablink instance."""
        return str(self._inner.Address)

    @property
    def name(self) -> str:
        """The name of the Lablink instance."""
        return self._inner.Name

    @property
    def version(self) -> str:
        """The version of the Lablink instance."""
        raise NotImplementedError
        return self._inner.Version

    @property
    def serial_number(self) -> str:
        """The serial number of the Lablink instance."""
        return self._inner.Serial
