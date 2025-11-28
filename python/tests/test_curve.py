from __future__ import annotations

from math import isnan

import pytest


@pytest.fixture
def curve_noise(data_noise_test):
    return data_noise_test[0].curves[0]


@pytest.fixture
def curve_dpv(data_dpv):
    return data_dpv[0].curves[0]


@pytest.fixture
def curve_cv(data_cv):
    return data_cv[0].curves[0]


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
        1.4645238461538463,
        12.20311125,
        33.24060953488372,
    ]
    assert peaks[0].curve_title == curve_dpv.title

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
    assert peaks[0].curve_title == curve.title

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
    assert not curve_dpv.reference_electrode_name
    assert not curve_dpv.reference_electrode_potential
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
    assert curve_dpv._pscurve is not new_curve._pscurve
    assert curve_dpv._pscurve.XAxisDataArray is not new_curve._pscurve.XAxisDataArray
    assert curve_dpv._pscurve.YAxisDataArray is not new_curve._pscurve.YAxisDataArray
