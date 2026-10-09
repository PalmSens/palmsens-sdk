import pytest

from pypalmsens.lablink._client import HttpClient


@pytest.mark.asyncio
async def test_https():
    client = HttpClient('https://127.0.0.1/api/v1/')
    r = await client.get('/Home/GetInfo')

    assert r.is_success
    assert r.json()


@pytest.mark.asyncio
async def test_http():
    client = HttpClient('http://127.0.0.1/api/v1/')
    r = await client.get('/Home/GetInfo')

    assert r.is_success
    assert r.json()
