from pspython.methods._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
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


def test_current_ranges_enum():
    cr = CURRENT_RANGE.cr_1_A

    psobj = cr.to_psobj()

    cr2 = CURRENT_RANGE.from_psobj(psobj)
    assert cr2 == cr


def test_potential_ranges_enum():
    pr = POTENTIAL_RANGE.pr_1_V

    psobj = pr.to_psobj()

    pr2 = POTENTIAL_RANGE.from_psobj(psobj)
    assert pr2 == pr
