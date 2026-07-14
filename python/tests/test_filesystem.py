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


def test_exists(fs): ...


def test_load_measurement(fs): ...


def test_remove(fs): ...


def test_clear(fs): ...


def test_free(fs):
    assert fs.free()


def test_size(fs):
    assert fs.size()


def test_timestamp_of(fs):
    ret = SimpleNamespace(Timestamp=DateTime.Now)

    with mock.patch.object(fs, '_get_device_file', return_value=ret):
        timestamp = fs.timestamp_of('foo.dmeas')
        assert datetime.fromisoformat(timestamp)


def test_size_of(fs):
    ret = SimpleNamespace(Size=123)

    with mock.patch.object(fs, '_get_device_file', return_value=ret):
        assert fs.size_of('foo.dmeas') == 123


def test_read_text(fs):
    ret = SimpleNamespace(Content='hello world')

    with mock.patch.object(fs, '_get_device_file', return_value=ret):
        assert fs.read_text('foo.dmeas') == 'hello world'


def test_tree(fs):
    assert fs.tree()


def test_iterdir(fs):
    assert list(fs.iterdir())
