from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

import pypalmsens as ps

DATA_DIR = Path(__file__).parent / 'test_data'

DATA_DPV = DATA_DIR / 'DPV example.pssession'
DATA_CV = DATA_DIR / 'CV example.pssession'
DATA_DIFF_PULSE = DATA_DIR / 'PSDiffPulse.pssession'
DATA_NOISE_TEST = DATA_DIR / 'PSNoiseTest.pssession'
DATA_CV_1SCAN = DATA_DIR / 'cv_1scan.pssession'
DATA_CV_1SCAN_BIPOT = DATA_DIR / 'cv_1scan_bipot.pssession'
DATA_CV_3SCAN = DATA_DIR / 'cv_3scan.pssession'
DATA_EIS_3CH_4SCAN_5FREQ = DATA_DIR / 'eis_3ch_4scan_5freq.pssession'
DATA_EIS_5FREQ = DATA_DIR / 'eis_5freq.pssession'


TESTS = Path(__file__).parent


@dataclass(frozen=True)
class Suite:
    name: str
    short: str
    subdir: str
    default: bool
    description: str


SUITES: list[Suite] = [
    Suite(
        name='offline',
        short='O',
        subdir='offline',
        default=True,
        description='offline logic: data structures, IO, methods, dataclasses',
    ),
    Suite(
        name='instrument',
        short='I',
        subdir='instrument',
        default=False,
        description='requires an instrument connected over USB',
    ),
    Suite(
        name='lablink',
        short='L',
        subdir='lablink',
        default=False,
        description='requires a running lablink server with an attached instrument',
    ),
]


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup('suites', 'test suite selection')
    for suite in SUITES:
        group.addoption(
            f'-{suite.short}',
            f'--{suite.name}',
            action='store_true',
            help=f'{suite.description}{" [default]" if suite.default else ""}',
        )


def pytest_configure(config: pytest.Config) -> None:
    for suite in SUITES:
        config.addinivalue_line('markers', f'{suite.name}: {suite.description}')


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # collect suites
    flagged = {suite.name for suite in SUITES if config.getoption(suite.name)}
    if flagged:  # explicit flags win
        wanted: set[str] | None = flagged
    elif any(not arg.startswith('-') for arg in config.invocation_params.args):
        wanted = None  # explicit path: run what was collected
    else:
        wanted = {suite.name for suite in SUITES if suite.default}

    # tag each item with its suite, and partition
    kept: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        path = Path(item.path).resolve()
        for suite in SUITES:
            if path.is_relative_to(TESTS / suite.subdir):
                # `name` is now the item's suite
                break
        else:
            raise pytest.UsageError(
                f'{item.nodeid} is not inside a known suite directory '
                f'({", ".join(suite.subdir for suite in SUITES)}). '
                'Move the file into a suite directory, or add one to SUITES.'
            )

        # so `-m lablink` works
        item.add_marker(getattr(pytest.mark, suite.name))
        if wanted is not None and suite.name not in wanted:
            deselected.append(item)
        else:
            kept.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept


@pytest.fixture(scope='module')
def measurement_dpv():
    return ps.load_measurement(DATA_DPV)


@pytest.fixture(scope='module')
def measurement_cv():
    return ps.load_measurement(DATA_CV)


@pytest.fixture(scope='module')
def measurement_diff_pulse():
    return ps.load_measurement(DATA_DIFF_PULSE)


@pytest.fixture(scope='module')
def measurement_noise_test():
    return ps.load_measurement(DATA_NOISE_TEST)


@pytest.fixture(scope='module')
def measurement_cv_1scan():
    return ps.load_measurement(DATA_CV_1SCAN)


@pytest.fixture(scope='module')
def measurement_cv_1scan_bipot():
    return ps.load_measurement(DATA_CV_1SCAN_BIPOT)


@pytest.fixture(scope='module')
def measurement_cv_3scan():
    return ps.load_measurement(DATA_CV_3SCAN)


@pytest.fixture(scope='module')
def measurement_eis_5freq():
    return ps.load_measurement(DATA_EIS_5FREQ)


@pytest.fixture(scope='module')
def measurement_eis_3ch_4scan_5freq():
    return ps.load_measurement(DATA_EIS_3CH_4SCAN_5FREQ)
