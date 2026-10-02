import ssl
from importlib.resources import files
from typing import Any

import httpx2

LABLINK_ROOT_CERT = files('pypalmsens.lablink.certs') / 'lablink-root-ca.pem'


class LablinkError(ConnectionError): ...


class LablinkAuthError(LablinkError): ...


class LablinkConnectionError(LablinkError): ...


class LablinkApiError(LablinkError): ...


class HttpClient:
    SNI: str = 'lablink.local'

    def __init__(self, base_url: str, token: str | None = None):
        ctx = ssl.create_default_context(cafile=str(LABLINK_ROOT_CERT))
        # lablink CA lacks keyUsage (Python 3.13+)
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT

        self._client = httpx2.Client(base_url=base_url, timeout=10.0, verify=ctx)
        self._client.headers['Host'] = 'lablink.local'

        self._token: str | None = None

        if token:
            self.set_token(token)

    async def request(self, method: str, path: str, **kwargs) -> Any:
        extensions = kwargs.pop('extensions', {})
        extensions['sni_hostname'] = self.SNI

        r = self._client.request(method, path, extensions=extensions, **kwargs)

        if r.is_error:
            raise LablinkApiError(r.reason_phrase)

        return r

    async def get(self, path: str, **kwargs) -> Any:
        return await self.request('GET', path, **kwargs)

    async def post(self, path: str, **kwargs) -> Any:
        return await self.request('POST', path, **kwargs)

    @property
    def authenticated(self) -> bool:
        return self._token is not None

    def set_token(self, token: str) -> None:
        """Store the token; applied to every subsequent request."""
        self._token = token
        self._client.headers['Authorization'] = f'Bearer {token}'

    async def close(self):
        await self._client.aclose()
