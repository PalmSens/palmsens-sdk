from pspython import pspyfiles
from pathlib import Path
import pytest


DATA_FILE = Path(__file__).parents[1] / "Demo CV DPV EIS IS-C electrode.pssession"


@pytest.fixture
def measurements():
    return pspyfiles.load_session_file(
        str(DATA_FILE),
        load_peak_data=True,
        load_eis_fits=True,
        return_dotnet_object=True,
    )


@pytest.fixture
def curve(measurements):
    return measurements[0].curves[0]


def test_curve_smooth(curve):
    x = curve.x_array
    y = curve.y_array

    curve.smooth(smooth_level=1)

    assert x == curve.x_array
    assert y != curve.y_array


def test_savitsky_golay(curve):
    x = curve.x_array
    y = curve.y_array

    curve.smooth(smooth_level=1)

    assert x == curve.x_array
    assert y != curve.y_array


def test_savitsky_golay(curve):
    x = curve.x_array
    y = curve.y_array

    curve.smooth(smooth_level=1)

    assert x == curve.x_array
    assert y != curve.y_array
