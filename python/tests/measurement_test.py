import pytest

from pspython.data.curve import Curve


@pytest.fixture
def measurement(data_dpv):
    return data_dpv[0]


def test_measurement_properties(measurement):
    assert measurement.title == 'Square Wave Voltammetry'
    assert isinstance(measurement.timestamp, str)

    peaks = measurement.peaks
    assert len(peaks) == 0

    assert len(measurement.eis_fit) == 0

    curves = measurement.curves
    assert len(curves) == 1
    assert isinstance(curves[0], Curve)
