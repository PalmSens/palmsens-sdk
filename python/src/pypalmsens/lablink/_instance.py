"""Submodule for discovering and connecting to Lablink instances.

Use [discover][] to find Lablink instances on the network.
[Instance][] is a discovered instance with basic metadata. Use
[login][] to start an authenticated session.

"""

from __future__ import annotations

from PalmSens.Sdk.Lablink.Example.Lablink.Services import Client as PSClient
from PalmSens.Sdk.Lablink.Example.Lablink.Services import LablinkFactory as PSLabLinkFactory

from . import _model
from ._client import HttpClient
from ._mapping import _to_lablink_info
from ._public import LablinkInfo
from ._session import Session

factory = PSLabLinkFactory(
    PSClient.LablinkHttpClientFactory(), PSClient.LablinkSignalRHubFactory()
)


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

    def __init__(self, address: str = 'https://127.0.0.1', port: int = 5000):
        self._address = address.rstrip('/')
        self._http = HttpClient(f'{self._address}/api/v1')
        self._info: LablinkInfo | None = None

    def __repr__(self) -> str:
        s = []

        if self._info:
            s.append(f'name={self._info.name!r}')
        s.append(f'address={self.address!r}')

        return f'{type(self).__name__}({", ".join(s)})'

    @property
    def address(self) -> str:
        """The address of the instance."""
        return str(self._address)

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
        self._info = _to_lablink_info(_model.LablinkInfoResult.model_validate(data.json()))
        return self._info

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
        data = await self._http.post(
            '/Auth/ApiKey', json={'UserName': name, 'Password': password}
        )
        auth = _model.AuthResponseModel.model_validate(data.json())
        assert auth.Token
        self._http.set_token(auth.Token)
        return Session._from_http(self._http)
