from __future__ import annotations

import logging
from datetime import datetime
from types import SimpleNamespace
from unittest import mock

import pytest

import pypalmsens as ps

if True:
    from System import DateTime

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def fs():
    instrument, *_ = ps.discover()
    with ps.connect(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield ps.DeviceFileSystem(mgr)


def test_truediv(fs):
    assert fs / 'Measurements' == ps.DevicePath('Measurements')


def test_root(fs):
    assert str(fs.root) == ''


def test_exists(fs):
    files = fs.listdir()

    for f in files:
        assert fs.exists(f)
        assert fs.exists(f.parent)
        assert not fs.exists(f.with_name('foo'))


def test_load_measurement(fs):
    for f in fs.walk():
        if f.suffix == '.dmeas':
            break

    measurement = fs.load_measurement(f)

    assert measurement.method
    assert measurement.curves


def test_remove(fs):
    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.DeleteDeviceFile.return_value = None

        fs.remove(path)

    mocked.ClientConnection.DeleteDeviceFile.assert_called_once_with(path)


def test_delete_all_files(fs):
    with mock.patch.object(fs.manager, '_comm') as mocked:
        fs.delete_all_files(confirm=False)

        mocked.ClientConnection.ClearDeviceFiles.assert_not_called()

        fs.delete_all_files(confirm=True)

        mocked.ClientConnection.ClearDeviceFiles.assert_called_once()


def test_free(fs):
    assert fs.free()


def test_size(fs):
    assert fs.size()


def test_timestamp_of(fs):
    ret = SimpleNamespace(Timestamp=DateTime.Now)

    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.GetDeviceFile.return_value = ret

        timestamp = fs.timestamp_of(path)
        assert datetime.fromisoformat(timestamp)

    mocked.ClientConnection.GetDeviceFile.assert_called_once_with(f'/{path}')


def test_size_of(fs):
    ret = SimpleNamespace(Size=123)

    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.GetDeviceFile.return_value = ret

        assert fs.size_of(path) == 123

    mocked.ClientConnection.GetDeviceFile.assert_called_once_with(f'/{path}')


def test_read_text(fs):
    ret = SimpleNamespace(Content='hello world')

    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.GetDeviceFile.return_value = ret

        assert fs.read_text(path) == 'hello world'

    mocked.ClientConnection.GetDeviceFile.assert_called_once_with(f'/{path}')


def test_iterdir(fs):
    assert fs.listdir()


def test_listdir(fs):
    assert list(fs.listdir())


def test_walk(fs):
    for item in fs.walk():
        assert isinstance(item, ps.DevicePath)
