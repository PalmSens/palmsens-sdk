"""Submodule for discovering and connecting to Lablink instances.

Use [discover][] to find Lablink instances on the network.
[Instance][] is a discovered instance with basic metadata. Use
[login][] to start an authenticated session.
"""

from __future__ import annotations

from ._client import HttpClient
from ._session import Session
from .models import LablinkInfo
from .models._wire import AuthRequestModel, AuthResponseModel


class Instance:
    """
    A reference to a Lablink instance.

    Exposes basic metadata through properties and provides
    [get_info][] to refresh that information. Use [login][] for
    an authenticated session.

    Parameters
    ----------
    address : str, optional
        The address of the instance (default is 'https://127.0.0.1').
    port : int, optional
        Port to use on the instance (default is 5000).
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

        May be stale or empty.

        See [get_info][] to (re)populate this.
        """
        return self._info

    async def get_info(self) -> LablinkInfo:
        """
        Fetch fresh metadata from the lablink server.

        Returns
        -------
        LablinkInfo
            Instance metadata including name, version and serial number.
        """
        data = await self._http.get('/Home/GetInfo')
        self._info = LablinkInfo.from_wire(data.json())
        return self._info

    async def register_new_user(self, name: str, password: str) -> None:
        """
        Register a new user account.

        Parameters
        ----------
        name : str
            The username for authentication.
        password : str
            The password for authentication.
        """
        payload = AuthRequestModel(UserName=name, Password=password).model_dump()

        await self._http.post('/Auth/Register', json=payload)

    async def login(self, name: str, password: str) -> Session:
        """Start an authenticated session with this lablink instance.

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
        payload = AuthRequestModel(UserName=name, Password=password).model_dump()

        data = await self._http.post('/Auth/ApiKey', json=payload)
        auth = AuthResponseModel.model_validate(data.json())
        assert auth.Token
        self._http.set_token(auth.Token)
        return Session._from_http(self._http)
