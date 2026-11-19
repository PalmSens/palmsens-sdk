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


@pytest.fixture
def current_array():
    """Current array with reading metadata, so the range and status accessors work."""
    return CurrentArray.with_readings(
        [1.0, 2.0, 3.0, 4.0],
        name='scan1channel1',
        current_range=['10uA', '10uA', '1uA', '1uA'],
        reading_status=['OK', 'Overload', 'Underload', 'OK'],
    )


@pytest.fixture
def potential_array():
    """Potential array with reading metadata."""
    return PotentialArray.with_readings(
        [0.0, 0.1, 0.2, 0.3],
        name='scan1channel1',
        potential_range='1V',
        reading_status='OK',
    )


def test_array_status(current_array):
    _ = current_array.current_range()
    _ = current_array.timing_status()
    _ = current_array.reading_status()


def test_current_array(current_array):
    assert isinstance(current_array, CurrentArray)

    n_points = len(current_array)

    assert len(current_array.current()) == n_points
    assert len(current_array.current_reading()) == n_points
    assert len(current_array.current_range()) == n_points
    assert len(current_array.reading_status()) == n_points
    assert len(current_array.timing_status()) == n_points

    d = current_array.to_dict()
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


def test_potential_array(potential_array):
    assert isinstance(potential_array, PotentialArray)

    n_points = len(potential_array)

    assert len(potential_array.potential()) == n_points
    assert len(potential_array.potential_reading()) == n_points
    assert len(potential_array.potential_range()) == n_points
    assert len(potential_array.reading_status()) == n_points
    assert len(potential_array.timing_status()) == n_points

    d = potential_array.to_dict()
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


def test_constructor_current_reading_fail():
    """Plain values carry no reading metadata, so the accessor raises."""
    arr = CurrentArray([1, 2, 3])

    with pytest.raises(AttributeError):
        _ = arr.current_reading()


def test_constructor_potential_reading_fail():
    """Plain values carry no reading metadata, so the accessor raises."""
    arr = PotentialArray([1, 2, 3])

    with pytest.raises(AttributeError):
        _ = arr.potential_reading()


def test_with_readings_current_defaults():
    """Omitted metadata falls back to 10mA / OK / OK."""
    arr = CurrentArray.with_readings([1.0, 2.0, 3.0])

    assert arr.current_range() == ['10mA', '10mA', '10mA']
    assert arr.reading_status() == ['OK', 'OK', 'OK']
    assert arr.timing_status() == ['OK', 'OK', 'OK']
    assert len(arr.current_reading()) == 3
    assert len(arr.to_dict()) == 5


def test_with_readings_potential_defaults():
    """Omitted metadata falls back to 1V / OK / OK."""
    arr = PotentialArray.with_readings([0.0, 0.1])

    assert arr.potential_range() == ['1V', '1V']
    assert arr.reading_status() == ['OK', 'OK']
    assert len(arr.potential_reading()) == 2
    assert len(arr.to_dict()) == 5


def test_current_array_reading_metadata():
    """Artificial array can carry per-point current ranges and reading statuses."""
    arr = CurrentArray.with_readings(
        [1.0, 2.0, 0.2],
        current_range=['10mA', '10mA', '1uA'],
        reading_status=['Underload', 'OK', 'OK'],
    )

    assert arr.current_range() == ['10mA', '10mA', '1uA']
    assert arr.reading_status() == ['Underload', 'OK', 'OK']
    assert arr.timing_status() == ['OK', 'OK', 'OK']

    assert arr.current() == [1.0, 2.0, 0.2]
    np.testing.assert_allclose(arr.current_in_range(), [0.0001, 0.0002, 0.2])

    assert len(arr.current_reading()) == 3
    assert len(arr.to_dict()) == 5


def test_current_array_reading_metadata_broadcast():
    """A single literal applies to every point."""
    arr = CurrentArray.with_readings([1.0, 2.0], current_range='1uA', reading_status='Overload')

    assert arr.current_range() == ['1uA', '1uA']
    assert arr.reading_status() == ['Overload', 'Overload']


def test_current_array_reading_metadata_length_mismatch():
    with pytest.raises(ValueError):
        _ = CurrentArray.with_readings([1.0, 2.0, 3.0], current_range=['1uA', '10uA'])


def test_potential_array_reading_metadata():
    """Artificial potential array exposes range and status metadata."""
    arr = PotentialArray.with_readings(
        [0.5, 0.75],
        potential_range='1V',
        reading_status=['OK', 'OverloadWarning'],
    )

    assert arr.potential_range() == ['1V', '1V']
    assert arr.reading_status() == ['OK', 'OverloadWarning']
    assert arr.potential_in_range() == [0.5, 0.75]
    assert len(arr.potential_reading()) == 2
    assert len(arr.to_dict()) == 5


def test_current_array_midc_metadata():
    """The mIDC in-range quirk reproduces without a session file.

    Mirrors test_current_array_midc, which validates the same behaviour against
    recorded EIS data.
    """
    midc = CurrentArray.with_readings([0.2, 0.5], array_type='miDC', current_range='10uA')

    assert isinstance(midc, CurrentArray)
    assert midc.type == 'miDC'

    assert midc.to_list() != midc.current()
    assert midc.to_list() == midc.current_in_range()


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
