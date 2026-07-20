from __future__ import annotations

import logging
from datetime import datetime
from types import SimpleNamespace
from unittest import mock

import pytest

import pypalmsens as ps
from pypalmsens._instruments import DevicePath

if True:
    from System import DateTime

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'parts,expected',
    (
        ([], ''),
        (['a'], 'a'),
        (['a', 'b'], 'a/b'),
        (['a', 'b/c.x'], 'a/b/c.x'),
        (['a', 'b/c.x'], 'a/b/c.x'),
        (['a/b', 'c.x'], 'a/b/c.x'),
        (['', 'c.x'], 'c.x'),
        (['a/b', ''], 'a/b'),
    ),
)
def test_device_path(parts, expected):
    p = DevicePath(*parts)
    assert p.__fspath__() == expected


@pytest.fixture(scope='module')
def fs():
    instruments = ps.discover()
    with ps.connect(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield ps.DeviceFileSystem(mgr)


@pytest.mark.instrument
def test_truediv(fs):
    assert fs / 'Measurements' == DevicePath('Measurements')


@pytest.mark.instrument
def test_root(fs):
    assert str(fs.root) == ''


@pytest.mark.instrument
def test_exists(fs):
    files = fs.listdir()

    for f in files:
        assert fs.exists(f)
        assert fs.exists(f.parent)
        assert not fs.exists(f.with_name('foo'))


@pytest.mark.instrument
def test_load_measurement(fs):
    files = fs.listdir()
    f = files[0]
    measurement = fs.load_measurement(f)

    assert measurement.method
    assert measurement.curves


@pytest.mark.instrument
def test_remove(fs):
    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.DeleteDeviceFile.return_value = None

        fs.remove(path)

    mocked.ClientConnection.DeleteDeviceFile.assert_called_once_with(path)


@pytest.mark.instrument
def test_delete_all_files(fs):
    with mock.patch.object(fs.manager, '_comm') as mocked:
        fs.delete_all_files(confirm=False)

        mocked.ClientConnection.ClearDeviceFiles.assert_not_called()

        fs.delete_all_files(confirm=True)

        mocked.ClientConnection.ClearDeviceFiles.assert_called_once()


@pytest.mark.instrument
def test_free(fs):
    assert fs.free()


@pytest.mark.instrument
def test_size(fs):
    assert fs.size()


@pytest.mark.instrument
def test_timestamp_of(fs):
    ret = SimpleNamespace(Timestamp=DateTime.Now)

    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.GetDeviceFile.return_value = ret

        timestamp = fs.timestamp_of(path)
        assert datetime.fromisoformat(timestamp)

    mocked.ClientConnection.GetDeviceFile.assert_called_once_with(f'/{path}')


@pytest.mark.instrument
def test_size_of(fs):
    ret = SimpleNamespace(Size=123)

    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.GetDeviceFile.return_value = ret

        assert fs.size_of(path) == 123

    mocked.ClientConnection.GetDeviceFile.assert_called_once_with(f'/{path}')


@pytest.mark.instrument
def test_read_text(fs):
    ret = SimpleNamespace(Content='hello world')

    path = 'foo.dmeas'

    with mock.patch.object(fs.manager, '_comm') as mocked:
        mocked.ClientConnection.GetDeviceFile.return_value = ret

        assert fs.read_text(path) == 'hello world'

    mocked.ClientConnection.GetDeviceFile.assert_called_once_with(f'/{path}')


@pytest.mark.instrument
def test_tree(fs):
    assert fs.tree()


@pytest.mark.instrument
def test_listdir(fs):
    assert list(fs.listdir())
