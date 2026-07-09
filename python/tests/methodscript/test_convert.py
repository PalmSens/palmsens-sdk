from __future__ import annotations

import pytest

import pypalmsens as ps


@pytest.mark.parametrize(
    'v,offset,expected',
    (
        (100, 0, '100'),
        (100, 3, '100k'),
        (100.0, -3, '100m'),
        (100.0, 18, '100E'),
        (100, -18, '100a'),
        (0.5, 0, '500m'),
        (0.0005, 0, '500u'),
        (0.0000005, 0, '500n'),
        (0.0000005, 3, '500u'),
        (0.123456789, 0, '123457u'),
        (123456789, 0, '123457k'),
        (0, 0, '0'),
        (-0, 3, '0'),
        (-1, 3, '-1k'),
    ),
)
def test_convert_to_ms_value(v: float, offset: int, expected: str):
    assert ps._methods.energy.convert_to_ms_value(v, offset=offset) == expected
