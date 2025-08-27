from __future__ import annotations

from pathlib import Path

import pytest

import pypalmsens

DATA_DIR = Path(__file__).parent / 'test_data'

DATA_DPV = DATA_DIR / 'DPV example.pssession'
DATA_CV = DATA_DIR / 'CV example.pssession'
DATA_DIFF_PULSE = DATA_DIR / 'PSDiffPulse.pssession'
DATA_NOISE_TEST = DATA_DIR / 'PSNoiseTest.pssession'
DATA_CV_1SCAN = DATA_DIR / 'cv_1scan.pssession'
DATA_CV_3SCAN = DATA_DIR / 'cv_3scan.pssession'
DATA_CV_1SCAN = DATA_DIR / 'cv_1scan.pssession'
DATA_CV_3SCAN = DATA_DIR / 'cv_3scan.pssession'
DATA_EIS_3CH_4SCAN_5FREQ = DATA_DIR / 'eis_3ch_4scan_5freq.pssession'
DATA_EIS_5FREQ = DATA_DIR / 'eis_5freq.pssession'


@pytest.fixture(scope='module')
def data_dpv():
    return pypalmsens.load_session_file(DATA_DPV)


@pytest.fixture(scope='module')
def data_cv():
    return pypalmsens.load_session_file(DATA_CV)


@pytest.fixture(scope='module')
def data_diff_pulse():
    return pypalmsens.load_session_file(DATA_DIFF_PULSE)


@pytest.fixture(scope='module')
def data_noise_test():
    return pypalmsens.load_session_file(DATA_NOISE_TEST)


@pytest.fixture(scope='module')
def data_cv_1scan():
    return pypalmsens.load_session_file(DATA_CV_1SCAN)


@pytest.fixture(scope='module')
def data_cv_3scan():
    return pypalmsens.load_session_file(DATA_CV_3SCAN)


@pytest.fixture(scope='module')
def data_eis_5freq():
    return pypalmsens.load_session_file(DATA_EIS_5FREQ)


@pytest.fixture(scope='module')
def data_eis_3ch_4scan_5freq():
    return pypalmsens.load_session_file(DATA_EIS_3CH_4SCAN_5FREQ)
