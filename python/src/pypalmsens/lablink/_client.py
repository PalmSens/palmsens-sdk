import ssl
from importlib.resources import files
from typing import Any

import httpx2
from PalmSens.Core.Domain import Resources as PSResources

LABLINK_ROOT_CERT = files('pypalmsens.lablink.certs') / 'lablink-root-ca.pem'


class LablinkError(ConnectionError): ...


class LablinkAuthError(LablinkError): ...


class LablinkConnectionError(LablinkError): ...


class LablinkApiError(LablinkError): ...


class HttpClient:
    SNI: str = 'lablink.local'

    def __init__(self, base_url: str, token: str | None = None):
        self.last_response: httpx2.Response = None

        # Server uses PalmSens' internal lablink CA (bundled, public)
        # and its certs only cover 'lablink.local', no IPs which is
        # what we connect to. So: verify against the lablink root,
        # dial the IP, but present 'lablink.local' as the TLS name.
        # VERIFY_X509_STRICT is off because the lablink root CA lacks keyUsage
        # (rejected by Python 3.13+ strict mode).
        ctx = ssl.create_default_context(cafile=str(LABLINK_ROOT_CERT))
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT

        self._client = httpx2.Client(base_url=base_url, timeout=10.0, verify=ctx)
        self._client.headers['Host'] = 'lablink.local'

        self._token: str | None = None

        if token:
            self.set_token(token)

    async def request(self, method: str, path: str, **kwargs) -> Any:
        extensions = kwargs.pop('extensions', {})
        extensions['sni_hostname'] = self.SNI

        response = self._client.request(method, path, extensions=extensions, **kwargs)

        self.last_response = response

        if response.is_error:
            self.raise_from_response(response)

        return response

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

    def raise_from_response(self, response: httpx2.Response) -> None:
        """Generates error from response."""
        try:
            exc = response.json()['exceptionMessage']
            key = exc['resourceKey']
            *_, resource = exc['resourceDictionaryName'].rsplit('.')
            message = getattr(getattr(PSResources, resource), key)
            if parameters := exc.get('parameters'):
                message += f'({parameters})'
        except (KeyError, AttributeError):
            raise LablinkApiError(response.reason_phrase)
        else:
            raise LablinkApiError(message)
