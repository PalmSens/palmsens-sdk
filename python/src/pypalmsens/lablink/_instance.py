"""Submodule for discovering and connecting to Lablink instances.

Use [discover][] to find Lablink instances on the network.
[Instance][] is a discovered instance with basic metadata. Use
[login][] to start an authenticated session.

"""

from __future__ import annotations

from typing import ClassVar, Self

import System
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels
from PalmSens.Sdk.Lablink.Example.Lablink.Services import Client as PSClient
from PalmSens.Sdk.Lablink.Example.Lablink.Services import LablinkFactory as PSLabLinkFactory

from .._instruments.shared import wrap_task
from ._session import Session

factory = PSLabLinkFactory(
    PSClient.LablinkHttpClientFactory(), PSClient.LablinkSignalRHubFactory()
)


async def discover() -> list[Instance]:
    """
    Discover Lablink instances.

    Returns
    -------
    list[Instance]
        A list of discovered Lablink instances.
    """
    devices: list[PSModels.LablinkInfo] = await wrap_task(PSLablink.Lablink.Discover())
    return [Instance._wrap(device) for device in devices]


class Instance:
    """
    A reference to a Lablink instance.

    A Lablink instance exposes its basic information
    through properties, along with [fetch_metadata][] to refresh
    that information and [login][] to start an authenticated session.

    Parameters
    ----------
    address : str, optional
        The address of the instance (default is 'https://127.0.0.1/').
    """

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
        """The address of the instance."""
        return str(self._inner.AddressUri)

    @property
    def name(self) -> str:
        """The name of the instance."""
        return self._inner.Name

    @property
    def version(self) -> str:
        """The version of the instance."""
        return self._inner.Version

    @property
    def serial_number(self) -> str:
        """The serial number of the instance."""
        return self._inner.Serial

    async def fetch_metadata(self):
        """Fetch metadata for this instance.

        Updates the name, version, and serial number with the latest values.
        """
        self._inner = await wrap_task(factory.GetLablinkInfo(self._inner.AddressUri))

    async def login(self, name: str, password: str) -> Session:
        """Log in to the Lablink instance.

        Parameters
        ----------
        name : str
            The username for authentication.
        password : str
            The password for authentication.

        Returns
        -------
        Session
            A new session object for this instance.
        """
        ref: PSLablink.Lablink = await wrap_task(factory.Login(self._inner, name, password))
        return Session._wrap(ref)
