from __future__ import annotations

import logging
from datetime import datetime
from types import SimpleNamespace
from unittest import mock

import pytest
import pytest_asyncio

import pypalmsens as ps
from pypalmsens._instruments import DevicePath

if True:
    from System import DateTime

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope='module')
async def fs():
    instruments = await ps.discover_async()
    async with await ps.connect_async(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield ps.DeviceFileSystemAsync(mgr)


@pytest.mark.instrument
def test_truediv(fs):
    assert fs / 'Measurements' == DevicePath('Measurements')


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_root(fs):
    assert str(fs.root) == ''


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_exists(fs):
    async for f in fs.iterdir():
        assert await fs.exists(f)
        assert await fs.exists(f.parent)
        assert not await fs.exists(f.with_name('foo'))


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_load_measurement(fs):
    async for f in fs.iterdir():
        if f.suffix == '.dmeas':
            break

    measurement = await fs.load_measurement(f)

    assert measurement.method
    assert measurement.curves


@pytest.mark.asyncio
@pytest.mark.skip(reason='No way of testing this.')
@pytest.mark.instrument
async def test_remove(fs):
    pass


@pytest.mark.asyncio
@pytest.mark.skip(reason='No way of testing this.')
@pytest.mark.instrument
async def test_delete_all_files(fs):
    pass


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_free(fs):
    assert await fs.free()


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_size(fs):
    assert await fs.size()


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_timestamp_of(fs):
    ret = SimpleNamespace(Timestamp=DateTime.Now)

    path = 'foo.dmeas'

    with mock.patch.object(fs, '_get_device_file', return_value=ret):
        timestamp = await fs.timestamp_of(path)
        assert datetime.fromisoformat(timestamp)


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_size_of(fs):
    ret = SimpleNamespace(Size=123)

    path = 'foo.dmeas'

    with mock.patch.object(fs, '_get_device_file', return_value=ret):
        assert await fs.size_of(path) == 123


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_read_text(fs):
    ret = SimpleNamespace(Content='hello world')

    path = 'foo.dmeas'

    with mock.patch.object(fs, '_get_device_file', return_value=ret):
        assert await fs.read_text(path) == 'hello world'


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_iterdir(fs):
    assert await fs.listdir()


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_listdir(fs):
    async for item in fs.iterdir():
        assert item


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_walk(fs):
    async for item in fs.walk():
        assert isinstance(item, DevicePath)
