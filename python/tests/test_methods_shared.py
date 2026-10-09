from __future__ import annotations

import pytest

from pypalmsens._converters import (
    cr_enum_to_string,
    cr_string_to_enum,
    cr_string_to_sig_exp,
    frexp10,
    pr_enum_to_string,
    pr_string_to_enum,
    pr_string_to_sig_exp,
)
from pypalmsens._methods.levels import (
    convert_bools_to_int,
    convert_int_to_bools,
)


def test_convert_bool_list_to_int():
    assert convert_bools_to_int((True, False, True, False)) == 5
    assert convert_bools_to_int((False, True, False, True)) == 10
    assert convert_bools_to_int((False, False, False, False)) == 0
    assert convert_bools_to_int((True, True, True, True)) == 15


def test_convert_int_to_bool_list():
    assert convert_int_to_bools(5) == (True, False, True, False)
    assert convert_int_to_bools(10) == (False, True, False, True)
    assert convert_int_to_bools(0) == (False, False, False, False)
    assert convert_int_to_bools(15) == (True, True, True, True)


def test_current_range_enum():
    cr = '1A'
    enum = cr_string_to_enum(cr)
    cr2 = cr_enum_to_string(enum)
    assert cr2 == cr


def test_potential_ranges_enum():
    pr = '1V'
    enum = pr_string_to_enum(pr)
    pr2 = pr_enum_to_string(enum)
    assert pr2 == pr


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (0.001, (1, -3)),
        (0.000005, (5, -6)),
        (1000, (1, 3)),
        (5000, (5, 3)),
        (1, (1, 0)),
        (10, (1, 1)),
        (100, (1, 2)),
        (0.1, (1, -1)),
        (12345, (1, 4)),
    ],
)
def test_frexp10(value: float, expected: tuple[int, int]) -> None:
    assert frexp10(value) == expected


def test_current_range_sig_exp():
    cr = '1A'
    sig, exp = cr_string_to_sig_exp(cr)
    assert (sig, exp) == (1, 0)


def test_potential_ranges_sig_exp():
    pr = '1V'
    sig, exp = pr_string_to_sig_exp(pr)
    assert (sig, exp) == (1, 0)
