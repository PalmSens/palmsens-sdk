import pytest

from pypalmsens import lablink


@pytest.mark.lablink
@pytest.mark.asyncio
async def test_discover():
    instances = await lablink.discover()
    assert instances
    assert all(instance.name for instance in instances)


@pytest.mark.lablink
@pytest.mark.asyncio
async def test_metadata():
    local = lablink.Instance('https://127.0.0.1/')
    assert not local.name
    assert not local.version
    assert not local.serial_number
    await local.fetch_metadata()
    assert local.name
    assert local.version
    assert local.serial_number
