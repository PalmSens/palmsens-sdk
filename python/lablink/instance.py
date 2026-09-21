from __future__ import annotations

from typing import ClassVar, Self

import System
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels
from PalmSens.Sdk.Lablink.Example.Lablink.Services import Client as PSClient
from PalmSens.Sdk.Lablink.Example.Lablink.Services import LablinkFactory as PSLabLinkFactory
from session import Session

from pypalmsens._instruments.shared import create_future

factory = PSLabLinkFactory(
    PSClient.LablinkHttpClientFactory(), PSClient.LablinkSignalRHubFactory()
)


async def discover() -> list[Instance]:
    devices = await create_future(PSLablink.Lablink.Discover())
    return [Instance._wrap(device) for device in devices]


class Instance:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSModels.LablinkInfo

    def __init__(self, address: str = 'https://127.0.0.1/'):
        uri = System.Uri(address)
        self._inner = PSModels.LablinkInfo(uri)

    @classmethod
    def _wrap(cls, inner: PSModels.LablinkInfo) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    def __repr__(self) -> str:
        s = []

        if name := self.name:
            s.append(f'name={name!r}')
        s.append(f'address={self.address!r}')

        return f'{type(self).__name__}({", ".join(s)}'

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

    async def fetch_metadata(self):
        """Fetch metadata (name, version, serial) for this instance."""
        self._inner = await create_future(factory.GetLablinkInfo(self._inner.AddressUri))

    async def login(self, name: str, password: str) -> Session:
        ref = await create_future(factory.Login(self._inner, name, password))
        return Session._wrap(ref)
