from pathlib import Path

import pytest

from pspython.pspyfiles import load_session_file

DATA_DIR = Path(__file__).parent / 'test_data'

DATA_DPV = DATA_DIR / 'DPV example.pssession'
DATA_DIFF_PULSE = DATA_DIR / 'PSDiffPulse.pssession'
DATA_NOISE_TEST = DATA_DIR / 'PSNoiseTest.pssession'
DATA_CV_1SCAN = DATA_DIR / 'cv_1scan.pssession'
DATA_CV_3SCAN = DATA_DIR / 'cv_3scan.pssession'


@pytest.fixture(scope='module')
def data_dpv():
    return load_session_file(
        str(DATA_DPV),
    )


@pytest.fixture(scope='module')
def data_diff_pulse():
    return load_session_file(
        str(DATA_DIFF_PULSE),
    )


@pytest.fixture(scope='module')
def data_noise_test():
    return load_session_file(
        str(DATA_NOISE_TEST),
    )


@pytest.fixture(scope='module')
def data_cv_1scan():
    return load_session_file(
        str(DATA_CV_1SCAN),
    )


@pytest.fixture(scope='module')
def data_cv_3scan():
    return load_session_file(str(DATA_CV_3SCAN))
