"""Submodule for managing sessions on a Lablink instance.

Use [Session][] for an authenticated connection to a Lablink
instance. Use [ClaimBatch][] to group several instrument claims so
they can be released together.

"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Self, overload, override

import System
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData

from .._instruments.shared import wrap_task
from ..types import MethodTypeCompatible
from . import _model
from ._client import HttpClient
from ._instrument import InstrumentClaim, InstrumentRef
from ._mapping import _to_info
from ._measurement import Measurement, MeasurementJob, MeasurementRef
from ._model import (
    EmptyProperty,
    MeasurementListResult,
    MeasurementResult,
    SimpleInstrumentsCommand,
)
from ._public import LablinkInfo


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

    def __init__(
        self,
        address: str,
        token: str,
        port: int = 5000,
    ):
        self._http = HttpClient(f'{self._address}:{port}/api/v1', token=token)
        self._instruments = []
        self._info = None

    @classmethod
    def _from_http(cls, http: HttpClient) -> Self:
        obj = object.__new__(cls)
        obj._http = http
        obj._instruments = []
        obj._info = None
        return obj

    def __repr__(self) -> str:
        s = []

        # if name := self.name:
        #     s.append(f'name={name!r}')
        # s.append(f'address={self.address!r}')

        return f'{type(self).__name__}({", ".join(s)})'

    @property
    def instruments(self) -> list[InstrumentRef]:
        """The instruments from the most recent [list_instruments][] call.

        May be stale or empty.
        """
        return self._instruments

    async def list_instruments(self) -> list[InstrumentRef]:
        """List currently attached instruments.

        Refreshes the [instruments][] list.

        Returns
        -------
        list of InstrumentRef
            A list of currently attached instruments.
        """
        data = await self._http.get('/Instruments')
        # TODO: Just pass the instrument serial + metadata
        # InstrumentRef should be responsible for managing its metadata
        # for info in data:
        #     instrument = InstrumentRef(info['Serial'])
        #     instrument._info = info
        #
        instruments = [InstrumentRef._wrap(instrument) for instrument in data.json()]
        self._instruments = instruments
        return instruments

    async def _claim(self, instruments: Sequence[InstrumentRef]) -> list[InstrumentClaim]:
        props = {instrument.serial_number: EmptyProperty() for instrument in instruments}
        payload = SimpleInstrumentsCommand(
            InstrumentProperties=props, AllInstrumentsMustSucceed=True
        )

        await self._http.post('/Instruments/Claim', json=payload.model_dump())

        return [
            InstrumentClaim._wrap(instrument.serial_number, self) for instrument in instruments
        ]

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

    async def _release(self, instruments: Sequence[InstrumentRef]) -> None:
        props = {instrument.serial_number: EmptyProperty() for instrument in instruments}
        payload = SimpleInstrumentsCommand(
            InstrumentProperties=props, AllInstrumentsMustSucceed=True
        )

        await self._http.post('/Instruments/UnClaim', json=payload.model_dump())

    async def release(self, instrument: InstrumentRef) -> None:
        """Releaes an instrument.

        Parameters
        ----------
        instrument : InstrumentRef
            The instrument to release.
        """
        await self._release([instrument])

    async def release_many(self, instruments: Sequence[InstrumentRef]) -> None:
        """Release multiple instruments.

        Parameters
        ----------
        instruments : Sequence of InstrumentRef
            The instruments to release.
        """
        await self._release(instruments)

    async def list_measurements(self) -> list[MeasurementRef]:
        """List all measurements.

        Returns
        -------
        list of MeasurementRef
            A list of measurement references.
        """
        data = await self._http.get('/Measurements')
        refs = [MeasurementListResult.model_validate(item) for item in data.json()]
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
        import numpy as np

        resp = await self._http.get(f'/Measurements/{measurement.guid}')
        parsed = MeasurementResult.model_validate(resp.json())

        assert parsed.RawDataSets

        dataset, *_ = parsed.RawDataSets
        dataset_id = dataset.DataSetId

        print()

        assert dataset.DataArrays

        for array in dataset.DataArrays:
            array_type = array.DataValueType.name
            print(array_type)
            array_id = array.DataArrayId
            values_id = array.DataValuesId

            resp = await self._http.get(f'DataSets/{dataset_id}/{values_id}')
            raw = resp.content

            if array_type == 'CurrentRange':
                pairs = np.frombuffer(raw, dtype=np.int32).reshape(-1, 2)
                data = pairs[:, 0]
                other = pairs[:, 0]  # ?? factor? exponent?

            elif array_type in (
                'AppliedPotential',
                'Charge',
                'MeasuredCurrent',
                'AuxiliaryPotential',
                'ReverseCurrent',
                'ForwardCurrent',
            ):
                data = np.frombuffer(raw, dtype=np.float64)  # little-endian float64

            elif array_type in (
                'TimingStatus',
                'CurrentReadingStatus',
                'ForwardCurrentReadingStatus',
                'ReverseCurrentReadingStatus',
            ):
                data = np.frombuffer(raw, dtype=np.int8)  # int enum (8-bit signed integer)

            elif array_type in ('Index', 'CycleIndex', 'LevelIndex'):
                data = np.frombuffer(raw, dtype=np.int32)  # int enum (32 bit signed)

            elif array_type == 'Timestamp':
                ticks = np.frombuffer(raw, dtype=np.int64)  # 100-ns ticks
                data = ticks * 1e-7  # seconds

            else:
                print(len(resp.content))
                print(resp.content[:32].hex())
                data = '???'

            print(data, len(data))
            print()

        return Measurement._wrap(data)

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
    def info(self) -> LablinkInfo | None:
        """Last fetched metadata, or `None` if not yet fetched.

        See [fetch_metadata][] to (re)populate this.
        """
        return self._info

    async def fetch_metadata(self) -> LablinkInfo:
        """Fetch metadata for this instance.

        Updates the name, version, and serial number with the latest values.
        """
        data = await self._http.get('/Home/GetInfo')
        self._info = _to_info(_model.LablinkInfoResult.model_validate(data.json()))
        return self._info
