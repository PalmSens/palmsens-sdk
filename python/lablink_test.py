from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import datetime
from typing import ClassVar, Literal, Self

import nest_asyncio

import pypalmsens as ps
from pypalmsens._instruments.shared import create_future
from pypalmsens.types import AllowedMethods, MethodTypeCompatible

nest_asyncio.apply()

import System
from PalmSens import Method as PSMethod
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels
from PalmSens.Sdk.Lablink.Example.Lablink.Models import Data as PSData
from PalmSens.Sdk.Lablink.Example.Lablink.Services import Client as PSClient
from PalmSens.Sdk.Lablink.Example.Lablink.Services import LablinkFactory as PSLabLinkFactory

factory = PSLabLinkFactory(
    PSClient.LablinkHttpClientFactory(), PSClient.LablinkSignalRHubFactory()
)


class LablinkInfo:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSModels.LablinkInfo  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Lablink info cannot be instantiated directly. '
            'Obtain instances through `discover().'
        )

    @classmethod
    def _wrap(cls, inner: PSModels.LablinkInfo) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name}, address={self.address})'

    @classmethod
    async def from_uri(cls, address: str = 'https://127.0.0.1/') -> Self:
        address = System.Uri(address)
        inner = await create_future(factory.GetLablinkInfo(address))
        return cls._wrap(inner)

    @property
    def address(self) -> str:
        return str(self._inner.AddressUri)

    @property
    def name(self) -> str:
        return self._inner.Name

    @property
    def version(self) -> str:
        return self._inner.Version

    @property
    def serial_number(self) -> str:
        return self._inner.Serial

    async def login(self, name: str, password: str) -> Lablink:
        ref = await create_future(factory.Login(self._inner, name, password))
        return Lablink._wrap(ref)


class Lablink:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSLablink.Lablink  # pyright: ignore[reportUninitializedInstanceVariable]

    # Eventst
    # - _inner.OnInstrumentInfoChanged

    def __init__(self):
        raise TypeError(
            'Lablink instance cannot be instantiated directly. '
            'Obtain instances through `LablinkInfo.login()`.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name}, address={self.address})'

    @classmethod
    def _wrap(cls, inner: PSLablink.Lablink) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    async def refresh(self) -> list[InstrumentInfo]:
        """Refresh instrument listing?"""
        psinstruments = await create_future(self._inner.DiscoverInstruments())
        return [InstrumentInfo._wrap(psinstrument) for psinstrument in psinstruments]

    async def discover(self) -> list[LablinkInfo]:
        """Discover lablinks?"""
        refs = await create_future(self._inner.Discover())
        return [LablinkInfo._wrap(ref) for ref in refs]

    @property
    def instruments(self) -> list[InstrumentInfo]:
        """Return cached instrument listing?"""
        return [InstrumentInfo._wrap(refs) for refs in self._inner.Instruments]

    async def claim(self, instruments: Sequence[InstrumentInfo]) -> list[Instrument]:
        """Claims instrument."""
        lst = System.Collections.Generic.List[PSModels.LablinkInstrumentInfo]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        ref = await create_future(self._inner.ConnectInstruments(lst))

        return [Instrument._wrap(ref) for ref in ref]

    async def measurements(self) -> list[MeasurementInfo]:
        refs = await create_future(self._inner.GetMeasurements())
        return [MeasurementInfo._wrap(ref) for ref in refs]

    async def download_measurement(self, measurement: MeasurementInfo) -> LablinkMeasurement:
        """Not working, error: `InvalidOperationException: Sequence contains no matching element`

        https://stackoverflow.com/questions/3994336/sequence-contains-no-matching-element
        """
        ref = await create_future(self._inner.GetMeasurement(measurement._inner.Id))
        return LablinkMeasurement._wrap(ref)

    async def start_measurements(
        self, instruments: Sequence[Instrument], method: MethodTypeCompatible
    ) -> list[LablinkMeasurement]:
        """Not working, error: `unknown CellModeAfterMeasurement CellModePotentiostatic`"""
        lst = System.Collections.Generic.List[PSLablink.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        refs = await create_future(self._inner.StartMeasurements(lst, method._to_psmethod()))
        return [LablinkMeasurement._wrap(ref) for ref in refs]

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


class InstrumentInfo:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSModels.LablinkInstrumentInfo  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'InstrumentInfo cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name!r}, serial={self.serial_number!r})'

    @classmethod
    def _wrap(cls, inner: PSLablink.LablinkInstrumentInfo) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def name(self) -> str:
        return self.custom_name or self.default_name

    @property
    def custom_name(self) -> str | None:
        return self._inner.CustomInstrumentName

    @property
    def default_name(self) -> str:
        return self._inner.DefaultInstrumentName

    @property
    def is_claimed(self) -> bool:
        return self._inner.IsClaimed

    @property
    def claim_owner(self) -> str | None:
        return self._inner.ClaimOwnerUsername

    @property
    def status(self) -> Literal['Idle', 'Measuring', 'Error']:
        if self.is_in_error:
            return 'Error'
        elif self.is_measuring:
            return 'Measuring'
        else:
            return 'Idle'

    @property
    def is_in_error(self) -> bool:
        return self._inner.IsInErrorState

    @property
    def is_measuring(self) -> bool:
        return self._inner.IsMeasuring

    @property
    def model(self) -> str:
        return self._inner.Model

    @property
    def multichannel_id(self) -> str:
        return self._inner.MultiChannelId

    @property
    def multichannel_index(self) -> int:
        return self._inner.MultiChannelIndex

    @property
    def in_multichannel_group(self) -> bool:
        return self._inner.BelongsToMultiChannelInstrument

    @property
    def serial_number(self) -> str:
        return self._inner.Serial


class Instrument:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSLablink.LablinkInstrument  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'LablinkInstrument cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial_number={self.serial_number})'

    @classmethod
    def _wrap(cls, inner: PSLablink.LablinkInstrument) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def lablink(self) -> Lablink:
        return Lablink._wrap(self._inner.Parent)

    @property
    def serial_number(self) -> str:
        return self._inner.Serial


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


async def discover() -> list[LablinkInfo]:
    devices = await create_future(PSLablink.Lablink.Discover())
    return [LablinkInfo._wrap(device) for device in devices]


def a(f):
    return asyncio.run(create_future(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.CyclicVoltammetry()

    handles = await discover()

    for handle in handles:
        print(handle)

    local_handle = await LablinkInfo.from_uri('https://127.0.0.1/')

    lablink = await local_handle.login('test', 'test')

    instrument_handles = lablink.instruments

    for instrument_handle in instrument_handles:
        print(instrument_handle)

    measurements = await lablink.measurements()

    for measurement in measurements:
        print(measurement)

    instruments = await lablink.claim(instrument_handles)

    breakpoint()


if __name__ == '__main__':
    asyncio.run(main())
