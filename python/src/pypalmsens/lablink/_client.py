from typing import Any

import httpx


class LablinkError(ConnectionError): ...


class LablinkAuthError(LablinkError): ...


class LablinkConnectionError(LablinkError): ...


class LablinkApiError(LablinkError): ...


class HttpClient:
    def __init__(self, base_url: str, port: int = 5000, token: str | None = None):
        self._client = httpx.Client(base_url=base_url, timeout=10.0)
        self._token: str | None = None

        if token:
            self.set_token(token)

    async def request(self, method: str, path: str, **kwargs) -> Any:
        r = self._client.request(method, path, **kwargs)

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
