from __future__ import annotations

from math import isnan

import numpy as np
import pytest

from pypalmsens.data import CurrentArray, Curve, PotentialArray


@pytest.fixture
def curve():
    """Artificial curve with rising current on a potential ramp."""
    x = PotentialArray(np.linspace(-1.0, 0.0, 41))
    y = CurrentArray(np.linspace(1.0, 37.0, 41))
    return Curve(x, y, title='synthetic')


@pytest.fixture
def curve_peaks():
    """Artificial curve with peaks on a near-zero baseline, for baseline correction."""
    x_arr = np.linspace(-1.0, 0.0, 201)
    y_arr = (
        4.0 * np.exp(-(((x_arr + 0.8) / 0.05) ** 2))
        + 12.0 * np.exp(-(((x_arr + 0.5) / 0.05) ** 2))
        + 30.0 * np.exp(-(((x_arr + 0.3) / 0.05) ** 2))
    )
    return Curve(PotentialArray(x_arr), CurrentArray(y_arr), title='synthetic peaks')


@pytest.fixture
def curve_noise():
    """Artificial curve with deterministic noise, for the smoothing tests."""
    rng = np.random.default_rng(42)
    x_arr = np.linspace(-1.0, 0.0, 50)
    y_arr = 10.0 * np.sin(np.linspace(0.0, 6.0, 50)) + rng.normal(0.0, 1.0, 50)
    return Curve(PotentialArray(x_arr), CurrentArray(y_arr), title='synthetic noise')


@pytest.fixture
def curve_dpv(measurement_dpv):
    """Recorded DPV curve."""
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


def test_curve_copy(curve):
    new_curve = curve.copy()
    assert curve is not new_curve
    assert curve._inner is not new_curve._inner
    assert curve._inner.XAxisDataArray is not new_curve._inner.XAxisDataArray
    assert curve._inner.YAxisDataArray is not new_curve._inner.YAxisDataArray


def test_curve_add(curve):
    a = curve.copy()
    b = a + a

    result = a + b
    assert isinstance(result, Curve)
    assert len(result) == len(a)

    a_np = a.y_array.to_numpy()
    expected = a_np + b.y_array.to_numpy()
    np.testing.assert_allclose(result.y_array.to_numpy(), expected)


def test_curve_add_commutative(curve):
    a = curve.copy()
    b = a + a

    np.testing.assert_allclose(
        (a + b).y_array.to_numpy(),
        (b + a).y_array.to_numpy(),
    )


def test_curve_sub(curve):
    a = curve.copy()
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


def test_curve_rsub_direction(curve):
    """__rsub__ must compute other - self (operands reversed vs __sub__)."""
    a = curve.copy()
    b = a + a

    result = type(curve).__rsub__(a, b)

    np.testing.assert_allclose(result.y_array.to_numpy(), (b - a).y_array.to_numpy())


def test_curve_add_sub_types(curve):
    with pytest.raises(TypeError):
        _ = curve + 1
    with pytest.raises(TypeError):
        _ = curve - 1
    with pytest.raises(TypeError):
        _ = 1 - curve


def test_curve_remove_baseline(curve_peaks):
    corrected, baseline = curve_peaks.remove_baseline(max_sweeps=1001, window_size=2)

    assert baseline.title.endswith('(baseline)')
    assert corrected.title.endswith('(corrected)')

    assert list(corrected.x_array) == list(curve_peaks.x_array)
    assert list(baseline.x_array) == list(curve_peaks.x_array)

    assert list(corrected.y_array) != list(curve_peaks.y_array)
    assert list(baseline.y_array) != list(curve_peaks.y_array)

    assert sum(curve_peaks.y_array) > sum(corrected.y_array) > sum(baseline.y_array)


def test_concat(curve):
    c = curve.concat(curve)
    assert len(c) == 2 * len(curve)
    assert c.n_points == 2 * curve.n_points


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
