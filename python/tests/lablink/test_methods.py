from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from test_techniques import (
    ACV,
    CA,
    CC,
    CP,
    CV,
    DPV,
    EIS,
    FAM,
    FCV,
    FGIS,
    FIS,
    LSP,
    LSV,
    MA,
    MM,
    MP,
    MPAD,
    MS,
    NPV,
    OCP,
    PAD,
    SCP,
    SWV,
    EIS_pot_fixed,
    EIS_pot_scan,
    EIS_single_point,
    EIS_time_fixed,
    EIS_time_scan,
    GIS_cur_fixed,
    GIS_cur_scan,
    GIS_single_point,
    GIS_time_fixed,
    GIS_time_scan,
    LSV_aux,
)

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
    'method',
    (
        CV,
        pytest.param(FCV, marks=needs_technique_support('fcv')),
        LSV,
        LSV_aux,
        ACV,
        SWV,
        CP,
        pytest.param(SCP, marks=not_supported_by_device('StrippingChronoPotentiometry')),
        LSP,
        OCP,
        CA,
        FAM,
        DPV,
        PAD,
        pytest.param(MPAD, marks=not_supported_by_device('MultiplePulseAmperometry')),
        NPV,
        MA,
        MP,
        CC,
        EIS,
        pytest.param(EIS_pot_fixed, marks=NO_SCAN_TYPE),
        pytest.param(EIS_pot_scan, marks=NO_SCAN_TYPE),
        pytest.param(EIS_time_scan, marks=NO_SCAN_TYPE),
        pytest.param(EIS_time_fixed, marks=NO_SCAN_TYPE),
        pytest.param(EIS_single_point, marks=NO_FREQUENCY_TYPE),
        pytest.param(FIS, marks=needs_technique_support('fis')),
        pytest.param(GIS_cur_fixed, marks=NO_SCAN_TYPE),
        pytest.param(GIS_cur_scan, marks=NO_SCAN_TYPE),
        pytest.param(GIS_time_scan, marks=NO_SCAN_TYPE),
        pytest.param(GIS_time_fixed, marks=NO_SCAN_TYPE),
        pytest.param(GIS_single_point, marks=NO_FREQUENCY_TYPE),
        pytest.param(FGIS, marks=needs_technique_support('fgis')),
        MS,
        pytest.param(MM, marks=NO_IMPEDANCE_STAGE),
    ),
)
async def test_measurements(session: lablink.Session, method):
    params = BaseTechnique._registry[method.id].from_dict(method.kwargs)  # type: ignore

    [instrument] = session.instruments
    async with await instrument.claim() as claim:
        job = await claim.start_measurement(method=params)
        measurement = await job
    assert measurement
