from __future__ import annotations

import asyncio
from typing import ClassVar, Self

import nest_asyncio

from pypalmsens._instruments.shared import create_future

nest_asyncio.apply()

import System
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels
from PalmSens.Sdk.Lablink.Example.Lablink.Services import Client as PSClient
from PalmSens.Sdk.Lablink.Example.Lablink.Services import LablinkFactory as PSLabLinkFactory

factory = PSLabLinkFactory(
    PSClient.LablinkHttpClientFactory(), PSClient.LablinkSignalRHubFactory()
)


class LablinkDevice:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSModels.LablinkInfo  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Lablink info cannot be instantiated directly. '
            'Obtain instances through `discover()`.'
        )

    @classmethod
    def _wrap(cls, inner: PSModels.LablinkInfo) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'name={self.name}, '
            f'version={self.version}, '
            f'serial={self.serial}, '
            f'uri={self.uri})'
        )

    @classmethod
    async def from_uri(cls, uri: str = 'https://127.0.0.1/') -> Self:
        uri = System.Uri(uri)
        inner = await create_future(factory.GetLablinkInfo(uri))
        return cls._wrap(inner)

    @property
    def uri(self) -> str:
        return str(self._inner.AddressUri)

    @property
    def name(self) -> str:
        return self._inner.Name

    @property
    def version(self) -> str:
        return self._inner.Version

    @property
    def serial(self) -> str:
        return self._inner.Serial


async def discover() -> list[LablinkDevice]:
    devices = await create_future(PSLablink.Lablink.Discover())
    return [LablinkDevice._wrap(device) for device in devices]


async def main():
    lablinks = await discover()

    for lablink in lablinks:
        print(lablink)

    local = await LablinkDevice.from_uri('https://127.0.0.1/')

    breakpoint()


if __name__ == '__main__':
    asyncio.run(main())
