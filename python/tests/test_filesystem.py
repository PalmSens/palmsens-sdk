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


def test_truediv(fs):
    assert fs / 'Measurements' == DevicePath('Measurements')


def test_root(fs):
    assert str(fs.root) == ''


def test_exists(fs):
    files = list(fs.iterdir())

    f = files[0]

    assert fs.exists(f)
    assert fs.exists(f.parent)
    assert not fs.exists(fs.with_name('foo'))


def test_load_measurement(fs):
    f = next(fs.iterdir())
    measurement = fs.load_measurement(f)

    assert measurement.method
    assert measurement.curves


def test_remove(fs):
    ret = fs.remove('does_not_exist')
    assert ret is None

    path = 'foo.dmeas'

    with mock.patch.object(
        fs._client_connection, 'DeleteDeviceFile', return_value=None
    ) as mock_get:
        fs.remove(path)

    assert mock_get.assert_called_once_with(path)


def test_clear(fs):
    with mock.patch.object(
        fs._client_connection, 'ClearDeviceFiles', return_value=None
    ) as clear_method:
        fs.delete_all_files(confirm=False)
        fs.delete_all_files(confirm=True)

    assert clear_method.assert_called_once()


def test_free(fs):
    assert fs.free()


def test_size(fs):
    assert fs.size()


def test_timestamp_of(fs):
    ret = SimpleNamespace(Timestamp=DateTime.Now)

    path = 'foo.dmeas'

    with mock.patch.object(
        fs._client_connection, 'GetDeviceFile', return_value=ret
    ) as mock_get:
        timestamp = fs.timestamp_of(path)
        assert datetime.fromisoformat(timestamp)

    assert mock_get.assert_called_once_with(path)


def test_size_of(fs):
    ret = SimpleNamespace(Size=123)

    path = 'foo.dmeas'

    with mock.patch.object(
        fs._client_connection, 'GetDeviceFile', return_value=ret
    ) as mock_get:
        assert fs.size_of(path) == 123

    assert mock_get.assert_called_once_with(path)


def test_read_text(fs):
    ret = SimpleNamespace(Content='hello world')

    path = 'foo.dmeas'

    with mock.patch.object(
        fs._client_connection, 'GetDeviceFile', return_value=ret
    ) as mock_get:
        assert fs.read_text(path) == 'hello world'

    assert mock_get.assert_called_once_with(path)


def test_tree(fs):
    assert fs.tree()


def test_iterdir(fs):
    assert list(fs.iterdir())
