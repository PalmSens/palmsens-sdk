from pathlib import Path

import pytest

from pspython import pspyfiles

DATA_FILE = Path(__file__).parents[1] / 'Demo CV DPV EIS IS-C electrode.pssession'


@pytest.fixture
def measurements():
    return pspyfiles.load_session_file(
        str(DATA_FILE),
        load_peak_data=True,
        load_eis_fits=True,
        return_dotnet_object=True,
    )


@pytest.fixture
def curve_noise(data_noise_test):
    return data_noise_test[0].curves[0]


@pytest.fixture
def curve_dpv(data_dpv):
    return data_dpv[0].curves[0]


def test_curve_smooth(curve_noise):
    x = curve_noise.x_array
    y = curve_noise.y_array

    curve_noise.smooth(smooth_level=1)

    assert x == curve_noise.x_array
    assert y != curve_noise.y_array


def test_savitsky_golay(curve_noise):
    x = curve_noise.x_array
    y = curve_noise.y_array

    curve_noise.smooth(smooth_level=1)

    assert x == curve_noise.x_array
    assert y != curve_noise.y_array


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
