from __future__ import annotations

from math import isnan

import numpy as np
import pytest
from PalmSens import Data as PSData

from pypalmsens.data import CurrentArray, DataArray, PotentialArray


@pytest.fixture
def array(measurement_cv_1scan):
    """Recorded Charge array; keeps the tests that assert recorded values."""
    return measurement_cv_1scan.dataset.arrays()[-1]


@pytest.fixture
def data_array():
    """Artificial array for generic array behaviour tests."""
    rng = np.random.default_rng(7)
    values = np.linspace(1.0, 9.0, 41) + rng.normal(0.0, 0.6, 41)
    return DataArray(values, array_type='Charge', name='synthetic')


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


def test_to_numpy(data_array):
    arr = data_array.to_numpy()
    assert isinstance(arr, np.ndarray)
    assert arr.dtype is np.dtype(float)
    assert len(arr) == 41


def test_to_list(data_array):
    lst = data_array.to_list()
    assert isinstance(lst, list)
    assert all(isinstance(val, float) for val in lst)


def test_properties(array):
    assert array.name == 'scan1channel1'
    assert array.type == 'Charge'
    assert array.quantity == 'Charge'
    assert isnan(array.ocp_value)


def test_array_smooth(data_array):
    new_array = data_array.savitsky_golay()
    assert list(new_array) != list(data_array)
    assert new_array is not data_array


def test_array_copy(data_array):
    new_array = data_array.copy()
    assert list(data_array) == list(new_array)  # data must match
    assert data_array is not new_array
    assert data_array._inner is not new_array._inner


def test_array_status(measurement_cv_1scan):
    array, *_ = measurement_cv_1scan.dataset.arrays(type='Current')
    _ = array.current_range()
    _ = array.timing_status()
    _ = array.reading_status()


def test_current_array(measurement_cv_1scan):
    arr = measurement_cv_1scan.dataset['Current']
    assert isinstance(arr, CurrentArray)

    n_points = len(arr)

    assert len(arr.current()) == n_points
    assert len(arr.current_reading()) == n_points
    assert len(arr.current_range()) == n_points
    assert len(arr.reading_status()) == n_points
    assert len(arr.timing_status()) == n_points

    d = arr.to_dict()
    assert len(d) == 5


def test_array_add(data_array):
    a = data_array.copy()
    b = a + a

    result = a + b
    assert len(result) == len(a)

    a_np = a.to_numpy()
    expected = a_np + b.to_numpy()
    np.testing.assert_allclose(result.to_numpy(), expected)


def test_array_add_commutative(data_array):
    a = data_array.copy()
    b = a + a

    np.testing.assert_allclose(
        (a + b).to_numpy(),
        (b + a).to_numpy(),
    )


def test_array_sub(data_array):
    a = data_array.copy()
    b = a + a

    result = b - a
    assert len(result) == len(a)
    np.testing.assert_allclose(result.to_numpy(), a.to_numpy())

    reverse = a - b
    np.testing.assert_allclose(reverse.to_numpy(), -a.to_numpy())
    np.testing.assert_allclose(reverse.to_numpy(), -result.to_numpy())

    zero = a - a
    np.testing.assert_allclose(zero.to_numpy(), 0)


def test_array_rsub_direction(data_array):
    a = data_array.copy()
    b = a + a

    result = type(data_array).__rsub__(a, b)

    np.testing.assert_allclose(result.to_numpy(), (b - a).to_numpy())


def test_array_mul(data_array):
    a = data_array.copy()
    a_np = a.to_numpy()

    # value * array
    for value in (2.0, 3):
        result = a * value
        expected = a_np * value
        assert len(result) == len(a)
        np.testing.assert_allclose(result.to_numpy(), expected)

    # value * array
    np.testing.assert_allclose((1.23 * a).to_numpy(), a_np * 1.23)
    np.testing.assert_allclose((10 * a).to_numpy(), a_np * 10)


def test_array_ops_type_mismatch(data_array):
    """Operations against non-array / wrong-type operands are rejected."""
    with pytest.raises(TypeError):
        _ = data_array + 1
    with pytest.raises(TypeError):
        _ = data_array - 1
    with pytest.raises(TypeError):
        _ = data_array * 'x'
    with pytest.raises(TypeError):
        _ = 'x' * data_array


def test_array_normalize(data_array):
    assert data_array.min() != 0
    assert data_array.max() != 1

    a = data_array.normalize()

    assert a.min() == 0
    assert a.max() == 1


def test_current_array_midc(measurement_eis_5freq):
    """Regression test for midc bug.

    For miDC the array value is 'in range' instead of µA for backwards compatibility reasons.
    `current()` and `current_in_range()` should always return the correct values.
    """
    midc = measurement_eis_5freq.dataset['miDC']
    iac = measurement_eis_5freq.dataset['Iac']

    assert midc.to_list() != midc.current()
    assert midc.to_list() == midc.current_in_range()

    assert iac.to_list() == iac.current()
    assert iac.to_list() != iac.current_in_range()


def test_potential_array(measurement_cv_1scan):
    arr = measurement_cv_1scan.dataset['Potential']
    assert isinstance(arr, PotentialArray)

    n_points = len(arr)

    assert len(arr.potential()) == n_points
    assert len(arr.potential_reading()) == n_points
    assert len(arr.potential_range()) == n_points
    assert len(arr.reading_status()) == n_points
    assert len(arr.timing_status()) == n_points

    d = arr.to_dict()
    assert len(d) == 5


def test_constructor():
    arr = DataArray([1.0, 2.0, 3.0], array_type='Time', name='test')

    assert isinstance(arr, DataArray)
    assert len(arr) == 3
    assert arr.to_list() == [1.0, 2.0, 3.0]
    assert arr.name == 'test'
    assert arr.type == 'Time'
    assert arr.unit == 's'
    assert isinstance(arr._inner, PSData.DataArray)

    c_arr = CurrentArray([1, 2, 3])
    assert isinstance(c_arr._inner, PSData.DataArrayCurrents)
    assert c_arr.unit == 'µA'

    p_arr = PotentialArray([1, 2, 3])
    assert isinstance(p_arr._inner, PSData.DataArrayPotentials)
    assert p_arr.unit == 'V'

    g_arr = DataArray([1, 2, 3])
    assert g_arr.name == 'Generic'
    assert g_arr.type == 'Generic'
    assert g_arr.unit == 'Unknown'


@pytest.mark.xfail(reason='Constructor does initialize values as CurrentReading')
def test_constructor_current_reading_fail():
    arr = CurrentArray([1, 2, 3])
    _ = arr.current_reading()


@pytest.mark.xfail(reason='Constructor does initialize values as PotentialReading')
def test_constructor_potential_reading_fail():
    arr = PotentialArray([1, 2, 3])
    _ = arr.potential_reading()


def test_array_update():
    arr = DataArray([0, 0, 0])

    arr.update([4, 5, 6])
    assert list(arr) == [4, 5, 6]

    with pytest.raises(ValueError):
        arr.update([1, 2])

    with pytest.raises(ValueError):
        arr.update([1, 2, 3, 4])


def test_array_slice_assignment():
    arr = DataArray([0, 0, 0])

    arr[:] = [1, 2, 3]
    assert list(arr) == [1, 2, 3]

    arr[1:3] = [7, 8]
    assert list(arr) == [1, 7, 8]

    with pytest.raises(ValueError):
        arr[:] = [1, 2]


def test_array_slice_broadcast():
    arr = DataArray([0, 0, 0, 0])

    arr[1:3] = 123
    assert list(arr) == [0, 123, 123, 0]

    arr[:] = 7
    assert list(arr) == [7, 7, 7, 7]


def test_array_slice_sequence():
    arr = DataArray([0, 0, 0])

    arr[:] = [1, 2, 3]
    assert list(arr) == [1, 2, 3]

    with pytest.raises(ValueError):
        arr[1:3] = [9, 8, 7]
