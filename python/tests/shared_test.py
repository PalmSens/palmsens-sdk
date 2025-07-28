from pspython.methods._shared import convert_bools_to_int, convert_int_to_bools


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
