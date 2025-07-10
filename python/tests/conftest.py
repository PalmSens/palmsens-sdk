from pathlib import Path

import pytest

from pspython.pspyfiles import load_session_file

DATA_DIR = Path(__file__).parent / 'test_data'

DATA_DPV = DATA_DIR / 'DPV example.pssession '
DATA_DIFF_PULSE = DATA_DIR / 'PSDiffPulse.pssession '
DATA_NOISE_TEST = DATA_DIR / 'PSNoiseTest.pssession'


@pytest.fixture(scope='module')
def data_dpv():
    return load_session_file(
        str(DATA_DPV),
        load_peak_data=True,
        load_eis_fits=True,
        return_dotnet_object=True,
    )


@pytest.fixture(scope='module')
def data_diff_pulse():
    return load_session_file(
        str(DATA_DIFF_PULSE),
        load_peak_data=True,
        load_eis_fits=True,
        return_dotnet_object=True,
    )


@pytest.fixture(scope='module')
def data_noise_test():
    return load_session_file(
        str(DATA_NOISE_TEST),
        load_peak_data=True,
        load_eis_fits=True,
        return_dotnet_object=True,
    )
