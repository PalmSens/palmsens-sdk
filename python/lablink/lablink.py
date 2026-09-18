from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Self

import System
from instrument import InstrumentClaim, InstrumentRef
from measurement import Measurement, MeasurementInfo
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels
from PalmSens.Sdk.Lablink.Example.Lablink.Services import Client as PSClient
from PalmSens.Sdk.Lablink.Example.Lablink.Services import LablinkFactory as PSLabLinkFactory

from pypalmsens._instruments.shared import create_future
from pypalmsens.types import MethodTypeCompatible

factory = PSLabLinkFactory(
    PSClient.LablinkHttpClientFactory(), PSClient.LablinkSignalRHubFactory()
)


async def discover() -> list[Instance]:
    devices = await create_future(PSLablink.Lablink.Discover())
    return [Instance._wrap(device) for device in devices]


class Instance:
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

    async def login(self, name: str, password: str) -> Session:
        ref = await create_future(factory.Login(self._inner, name, password))
        return Session._wrap(ref)


class Session:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSLablink.Lablink  # pyright: ignore[reportUninitializedInstanceVariable]

    # Eventst
    # - _inner.OnInstrumentRefChanged

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

    async def refresh(self) -> list[InstrumentRef]:
        """Refresh instrument listing?"""
        psinstruments = await create_future(self._inner.DiscoverInstruments())
        return [InstrumentRef._wrap(psinstrument) for psinstrument in psinstruments]

    async def discover(self) -> list[Instance]:
        """Discover lablinks?"""
        refs = await create_future(self._inner.Discover())
        return [Instance._wrap(ref) for ref in refs]

    @property
    def instruments(self) -> list[InstrumentRef]:
        """Return cached instrument listing?"""
        return [InstrumentRef._wrap(refs) for refs in self._inner.Instruments]

    async def claim(self, instruments: Sequence[InstrumentRef]) -> list[InstrumentClaim]:
        """Claims instrument."""
        lst = System.Collections.Generic.List[PSModels.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        ref = await create_future(self._inner.ConnectInstruments(lst))

        return [InstrumentClaim._wrap(ref) for ref in ref]

    async def measurements(self) -> list[MeasurementInfo]:
        refs = await create_future(self._inner.GetMeasurements())
        return [MeasurementInfo._wrap(ref) for ref in refs]

    async def download_measurement(self, measurement: MeasurementInfo) -> Measurement:
        """Not working, error: `InvalidOperationException: Sequence contains no matching element`

        https://stackoverflow.com/questions/3994336/sequence-contains-no-matching-element
        """
        ref = await create_future(self._inner.GetMeasurement(measurement._inner.Id))
        return Measurement._wrap(ref)

    async def start_measurements(
        self, instruments: Sequence[InstrumentClaim], method: MethodTypeCompatible
    ) -> list[Measurement]:
        """Not working, error: `unknown CellModeAfterMeasurement CellModePotentiostatic`"""
        lst = System.Collections.Generic.List[PSLablink.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        refs = await create_future(self._inner.StartMeasurements(lst, method._to_psmethod()))
        return [Measurement._wrap(ref) for ref in refs]

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
