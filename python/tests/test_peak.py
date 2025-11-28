from __future__ import annotations

import pytest


@pytest.fixture
def peak(data_dpv):
    curve = data_dpv[0].curves[0]
    peaks = curve.find_peaks(
        min_peak_width=0,
        min_peak_height=0,
    )
    return peaks[0]


def test_peak_properties(peak):
    assert peak.curve_title == 'dpvexample'
    assert peak.x_unit == 'V'
    assert peak.y_unit == 'µA'
    assert peak.analyte_name is None
    assert peak.area == pytest.approx(0.08553185)
    assert peak.label == '1.465'
    assert peak.left_index == 25
    assert peak.left_x == -0.875
    assert peak.left_y == 3.21169
    assert peak.maximum_of_derivative_neg == pytest.approx(-44.9518)
    assert peak.maximum_of_derivative_pos == pytest.approx(23.90614)
    assert peak.maximum_of_derivative_sum == pytest.approx(68.8579)
    assert peak.notes is None
    assert peak.y_offset == pytest.approx(2.698976)
    assert peak.index == 37
    assert peak.type == 'AutoPeak'
    assert peak.value == pytest.approx(1.464524)
    assert peak.x == -0.815
    assert peak.y == 4.1635
    assert peak.right_index == 51
    assert peak.right_x == -0.745
    assert peak.right_y == 2.10081
    assert peak.width == pytest.approx(0.06)
