from __future__ import annotations

from pathlib import Path

import pytest

import pypalmsens as ps

# Shared fixtures live in tests/test_data; the docs reference that path in examples.
DATA_DIR = Path(__file__).parent.parent / 'test_data'

# These files are required where a license-gated PalmSens algorithm runs
# (peak detection, circuit fitting) or where recorded instrument metadata is
# asserted (current ranges, reading statuses, bipot arrays, device info).
DATA_DPV = DATA_DIR / 'DPV example.pssession'
DATA_CV = DATA_DIR / 'CV example.pssession'
DATA_CV_1SCAN = DATA_DIR / 'cv_1scan.pssession'
DATA_CV_1SCAN_BIPOT = DATA_DIR / 'cv_1scan_bipot.pssession'
DATA_EIS_3CH_4SCAN_5FREQ = DATA_DIR / 'eis_3ch_4scan_5freq.pssession'
DATA_EIS_5FREQ = DATA_DIR / 'eis_5freq.pssession'


@pytest.fixture(scope='module')
def measurement_dpv():
    return ps.load_measurement(DATA_DPV)


@pytest.fixture(scope='module')
def measurement_cv():
    return ps.load_measurement(DATA_CV)


@pytest.fixture(scope='module')
def measurement_cv_1scan():
    return ps.load_measurement(DATA_CV_1SCAN)


@pytest.fixture(scope='module')
def measurement_cv_1scan_bipot():
    return ps.load_measurement(DATA_CV_1SCAN_BIPOT)


@pytest.fixture(scope='module')
def measurement_eis_5freq():
    return ps.load_measurement(DATA_EIS_5FREQ)


@pytest.fixture(scope='module')
def measurement_eis_3ch_4scan_5freq():
    return ps.load_measurement(DATA_EIS_3CH_4SCAN_5FREQ)
