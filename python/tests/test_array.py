from __future__ import annotations

from math import isnan

import numpy as np
import pytest

from pypalmsens._data.shared import ArrayType


@pytest.fixture
def array(data_cv_1scan):
    return data_cv_1scan[0].dataset.arrays()[-1]


def test_sequence(array):
    assert len(array) == 41
    assert array[0] == 0.0
    assert array[12] == pytest.approx(-78.84567)  # 562483386
    assert array[-1] == array[40]
    assert array[-41] == array[0]
    with pytest.raises(IndexError):
        assert array[-42]
    with pytest.raises(IndexError):
        assert array[41]
    assert len(array[0:12:2]) == 6
    assert isinstance(repr(array), str)
    assert array.min() == pytest.approx(-83.096866)
    assert array.max() == pytest.approx(11.609434)


def test_to_numpy(array):
    arr = array.to_numpy()
    assert isinstance(arr, np.ndarray)
    assert arr.dtype is np.dtype(float)
    assert len(arr) == 41


def test_to_list(array):
    lst = array.to_list()
    assert isinstance(lst, list)
    assert all(isinstance(val, float) for val in lst)


def test_properties(array):
    assert array.name == 'scan1channel1'
    assert array.type is ArrayType.Charge
    assert array.quantity == 'Charge'
    assert isnan(array.ocp_value)


def test_array_smooth(array):
    new_array = array.savitsky_golay()
    assert list(new_array) != list(array)
    assert new_array is not array


def test_array_copy(array):
    new_array = array.copy()
    assert list(array) == list(new_array)  # data must match
    assert array is not new_array
    assert array._psarray is not new_array._psarray


def test_array_status(data_cv_1scan):
    array = data_cv_1scan[0].dataset.current_arrays()[0]
    _ = array.as_current_range()
    _ = array.as_timing_status()
    _ = array.as_reading_status()


def test_array_status_fail(data_cv_1scan):
    array = data_cv_1scan[0].dataset.potential_arrays()[0]
    with pytest.raises(ValueError):
        _ = array.as_current_range()
        _ = array.as_timing_status()
        _ = array.as_reading_status()
