from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from helpers.technique_specs import TECHNIQUE_SPECS

import pypalmsens as ps
from pypalmsens import lablink
from pypalmsens._instruments.shared import MethodIncompatibleError
from pypalmsens._methods import BaseTechnique
from pypalmsens.lablink._errors import LablinkClientError


@pytest_asyncio.fixture(scope='module')
async def session():
    session = await lablink.Instance().login('test', 'test')
    _ = await session.list_instruments()
    return session


@pytest.mark.lablink
@pytest.mark.asyncio
async def test_start_single(session: lablink.Session):
    [instrument] = session.instruments
    method = ps.ChronoAmperometry(run_time=0.1, interval_time=0.01)

    async with await instrument.claim() as claim:
        job = await claim.start_measurement(method=method)
        measurement = await job

    assert job.is_finished
    assert measurement


@pytest.mark.lablink
@pytest.mark.asyncio
async def test_start_many(session: lablink.Session):
    instruments = session.instruments
    method = ps.ChronoAmperometry(run_time=0.1, interval_time=0.01)

    async with await session.claim(instruments) as claims:
        jobs = await session.start_measurement(claims, method=method)
        measurements = await asyncio.gather(*jobs)

    assert measurements
    assert len(measurements) == len(instruments)
    assert all(job.is_finished for job in jobs)


@pytest.mark.lablink
@pytest.mark.asyncio
def needs_technique_support(technique_id: str):
    """Lablink has no implementation for this technique."""
    return pytest.mark.xfail(
        raises=NotImplementedError,
        reason=f'Lablink does not support {technique_id!r}',
    )


def not_supported_by_device(method_name: str, device: str = 'EmStat4LR'):
    """pypalmsens knows the method, but the attached device does not."""
    return pytest.mark.xfail(
        raises=MethodIncompatibleError,
        reason=f'{method_name} is not supported by {device}',
    )


NO_SCAN_TYPE = pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Lablink does not support 'scan_type'",
)
NO_FREQUENCY_TYPE = pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Lablink does not support 'frequency_type'",
)
COMMAND_UNSUPPORTED = pytest.mark.xfail(
    raises=LablinkClientError,
    reason='The Command Is Unsupported.',
)
NO_IMPEDANCE_STAGE = pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Lablink does not support the 'Impedance' stage",
)


@pytest.mark.lablink
@pytest.mark.asyncio
@pytest.mark.parametrize(
    'variant',
    (
        'cv',
        pytest.param('fcv', marks=needs_technique_support('fcv')),
        'lsv',
        'lsv_aux',
        'acv',
        'swv',
        'cp',
        pytest.param('scp', marks=not_supported_by_device('StrippingChronoPotentiometry')),
        'lsp',
        'ocp',
        'ca',
        'fam',
        'dpv',
        'pad',
        pytest.param('mpad', marks=not_supported_by_device('MultiplePulseAmperometry')),
        'npv',
        'ma',
        'mp',
        'cc',
        'eis',
        pytest.param('eis_pot_fixed', marks=NO_SCAN_TYPE),
        pytest.param('eis_pot_scan', marks=NO_SCAN_TYPE),
        pytest.param('eis_time_scan', marks=NO_SCAN_TYPE),
        pytest.param('eis_time_fixed', marks=NO_SCAN_TYPE),
        pytest.param('eis_single_point', marks=NO_FREQUENCY_TYPE),
        pytest.param('fis', marks=needs_technique_support('fis')),
        pytest.param('gis_cur_fixed', marks=NO_SCAN_TYPE),
        pytest.param('gis_cur_scan', marks=NO_SCAN_TYPE),
        pytest.param('gis_time_scan', marks=NO_SCAN_TYPE),
        pytest.param('gis_time_fixed', marks=NO_SCAN_TYPE),
        pytest.param('gis_single_point', marks=NO_FREQUENCY_TYPE),
        pytest.param('fgis', marks=needs_technique_support('fgis')),
        'ms',
        pytest.param('mm', marks=NO_IMPEDANCE_STAGE),
    ),
)
async def test_measurements(session: lablink.Session, variant):
    spec = TECHNIQUE_SPECS[variant]
    params = BaseTechnique._registry[spec.id].from_dict(spec.kwargs)  # type: ignore

    [instrument] = session.instruments
    async with await instrument.claim() as claim:
        job = await claim.start_measurement(method=params)
        measurement = await job
    assert measurement
