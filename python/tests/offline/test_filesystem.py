from __future__ import annotations

import logging

import pytest

import pypalmsens as ps

if True:
    pass

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'parts,expected',
    (
        ([], ''),
        (['a'], 'a'),
        (['a', 'b'], 'a/b'),
        (['a', 'b/c.x'], 'a/b/c.x'),
        (['a/b', 'c.x'], 'a/b/c.x'),
        (['', 'c.x'], 'c.x'),
        (['a/b', ''], 'a/b'),
    ),
)
def test_device_path(parts, expected):
    p = ps.DevicePath(*parts)
    assert p.__fspath__() == expected
