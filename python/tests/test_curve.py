from __future__ import annotations

from math import isnan

import numpy as np
import pytest

from pypalmsens.data import CurrentArray, Curve, PotentialArray


@pytest.fixture
def curve_noise(measurement_noise_test):
    return measurement_noise_test.curves[0]


@pytest.fixture
def curve_dpv(measurement_dpv):
    return measurement_dpv.curves[0]


@pytest.fixture
def curve_cv(measurement_cv):
    return measurement_cv.curves[0]


def test_curve_smooth(curve_noise):
    x = list(curve_noise.x_array)
    y = list(curve_noise.y_array)

    curve_noise.smooth(smooth_level=1)

    assert x == list(curve_noise.x_array)
    assert y != list(curve_noise.y_array)


def test_savitsky_golay(curve_noise):
    x = list(curve_noise.x_array)
    y = list(curve_noise.y_array)

    curve_noise.savitsky_golay(window_size=2)

    assert x == list(curve_noise.x_array)
    assert y != list(curve_noise.y_array)


def test_find_peaks(curve_dpv):
    peaks = curve_dpv.find_peaks(
        min_peak_width=0,
        min_peak_height=0,
    )

    assert len(peaks) == 3

    assert [peak.x for peak in peaks] == [-0.815, -0.47, -0.28]
    assert [peak.value for peak in peaks] == [
        1.4645238,
        12.203112,
        33.240610,
    ]

    curve_dpv.clear_peaks()
    assert not curve_dpv.peaks


def test_find_peaks_semiderivative(curve_cv):
    curve = curve_cv
    peaks = curve.find_peaks_semiderivative(
        min_peak_height=0,
    )

    assert len(peaks) == 2

    assert [peak.x for peak in peaks] == [0.284884, -0.0223047]
    assert [peak.y for peak in peaks] == [15.8404, -15.826]

    curve.clear_peaks()
    assert not curve.peaks


def test_curve_properties(curve_dpv):
    assert len(curve_dpv) == 201
    assert curve_dpv.n_points == 201

    assert curve_dpv.min_x == -1.0
    assert curve_dpv.max_x == 0.0
    assert curve_dpv.min_y == 1.93339
    assert curve_dpv.max_y == 36.5019

    assert curve_dpv.mux_channel == -1

    assert isnan(curve_dpv.ocp_value)
    assert curve_dpv.x_unit == 'V'
    assert curve_dpv.x_label == 'Potential'
    assert curve_dpv.y_unit == 'µA'
    assert curve_dpv.y_label == 'Current'
    assert not curve_dpv.z_unit
    assert curve_dpv.title == 'dpvexample'

    x_arr = curve_dpv.x_array
    y_arr = curve_dpv.y_array

    assert len(x_arr) == len(y_arr)

    assert curve_dpv.min_x == min(x_arr)
    assert curve_dpv.max_x == max(x_arr)
    assert curve_dpv.min_y == min(y_arr)
    assert curve_dpv.max_y == max(y_arr)


def test_curve_copy(curve_dpv):
    new_curve = curve_dpv.copy()
    assert curve_dpv is not new_curve
    assert curve_dpv._inner is not new_curve._inner
    assert curve_dpv._inner.XAxisDataArray is not new_curve._inner.XAxisDataArray
    assert curve_dpv._inner.YAxisDataArray is not new_curve._inner.YAxisDataArray


def test_curve_add(curve_dpv):
    a = curve_dpv.copy()
    b = a + a

    result = a + b
    assert isinstance(result, Curve)
    assert len(result) == len(a)

    a_np = a.y_array.to_numpy()
    expected = a_np + b.y_array.to_numpy()
    np.testing.assert_allclose(result.y_array.to_numpy(), expected)


def test_curve_add_commutative(curve_dpv):
    a = curve_dpv.copy()
    b = a + a

    np.testing.assert_allclose(
        (a + b).y_array.to_numpy(),
        (b + a).y_array.to_numpy(),
    )


def test_curve_sub(curve_dpv):
    a = curve_dpv.copy()
    b = a + a

    result = b - a
    assert isinstance(result, Curve)
    assert len(result) == len(a)
    np.testing.assert_allclose(result.y_array.to_numpy(), a.y_array.to_numpy())

    reverse = a - b
    np.testing.assert_allclose(reverse.y_array.to_numpy(), -a.y_array.to_numpy())
    np.testing.assert_allclose(reverse.y_array.to_numpy(), -result.y_array.to_numpy())

    zero = a - a
    np.testing.assert_allclose(zero.y_array.to_numpy(), 0)


def test_curve_rsub_direction(curve_dpv):
    """__rsub__ must compute other - self (operands reversed vs __sub__)."""
    a = curve_dpv.copy()
    b = a + a

    result = type(curve_dpv).__rsub__(a, b)

    np.testing.assert_allclose(result.y_array.to_numpy(), (b - a).y_array.to_numpy())


def test_curve_add_sub_types(curve_dpv):
    with pytest.raises(TypeError):
        _ = curve_dpv + 1
    with pytest.raises(TypeError):
        _ = curve_dpv - 1
    with pytest.raises(TypeError):
        _ = 1 - curve_dpv


def test_curve_remove_baseline(curve_dpv):
    corrected, baseline = curve_dpv.remove_baseline(max_sweeps=1001, window_size=2)

    assert baseline.title.endswith('(baseline)')
    assert corrected.title.endswith('(corrected)')

    assert list(corrected.x_array) == list(curve_dpv.x_array)
    assert list(baseline.x_array) == list(curve_dpv.x_array)

    assert list(corrected.y_array) != list(curve_dpv.y_array)
    assert list(baseline.y_array) != list(curve_dpv.y_array)

    assert sum(curve_dpv.y_array) > sum(corrected.y_array) > sum(baseline.y_array)


def test_concat(curve_dpv):
    c = curve_dpv.concat(curve_dpv)
    assert len(c) == 2 * len(curve_dpv)
    assert c.n_points == 2 * curve_dpv.n_points


def test_constructor():
    current = CurrentArray([1, 2, 3])
    potential = PotentialArray([1, 2, 3])
    curve = Curve(current, potential, title='my curve')

    assert curve.x_unit == 'µA'
    assert curve.y_unit == 'V'
    assert curve.title == 'my curve'
    assert len(curve) == 3

    assert isinstance(curve.x_array, CurrentArray)
    assert isinstance(curve.y_array, PotentialArray)
