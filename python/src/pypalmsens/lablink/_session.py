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
    """List of claimed instruments."""
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

    async def release(self):
        for claim in self.claims:
            await claim.release()


class Session:
    """Manage connection to lablink instance."""
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
        """Instruments seen by the most recent `list_instruments()` call.

        May be stale or empty.
        """
        return [InstrumentRef._wrap(refs) for refs in self._inner.Instruments]

    async def list_instruments(self) -> list[InstrumentRef]:
        """List currently attached instruments

        Refreshes `self.instruments`."""
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
        """Claims instrument."""
        [claim] = await self._claim([instrument])
        return claim

    async def claim_many(self, instruments: Sequence[InstrumentRef]) -> ClaimBatch:
        """Claims list of instruments."""
        claims = await self._claim(instruments)
        return ClaimBatch(claims)

    async def list_measurements(self) -> list[MeasurementRef]:
        refs: list[PSData.MeasurementInfo] = await wrap_task(self._inner.GetMeasurements())
        return [MeasurementRef._wrap(ref, self) for ref in refs]

    async def fetch_measurement(self, measurement: MeasurementRef) -> Measurement:
        """Fetch measurement data."""
        ref: PSData.LablinkMeasurement = await wrap_task(
            self._inner.GetMeasurement(measurement._inner.Id)
        )
        return Measurement._wrap(ref)

    async def start(
        self, instrument: InstrumentClaim, *, method: MethodTypeCompatible
    ) -> MeasurementJob:
        [measurement] = await self.start_many([instrument], method=method)
        return measurement

    async def start_many(
        self, instruments: Sequence[InstrumentClaim], *, method: MethodTypeCompatible
    ) -> list[MeasurementJob]:
        lst = System.Collections.Generic.List[PSLablink.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        refs: list[PSData.LablinkMeasurement] = await wrap_task(
            self._inner.StartMeasurements(lst, method._to_psmethod())
        )
        return [MeasurementJob(ref) for ref in refs]

    @property
    def address(self) -> str:
        return str(self._inner.Address)

    @property
    def name(self) -> str:
        return self._inner.Name

    @property
    def version(self) -> str:
        raise NotImplementedError
        return self._inner.Version

    @property
    def serial_number(self) -> str:
        return self._inner.Serial
