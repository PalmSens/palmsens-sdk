import pytest
import pytest_asyncio
import System
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

from pypalmsens import lablink
from pypalmsens._methods import BaseTechnique


@pytest_asyncio.fixture(scope='module')
async def session():
    session = await lablink.Instance().login('test', 'test')
    return session


@pytest.mark.lablink
@pytest.mark.asyncio
@pytest.mark.parametrize(
    'method',
    (
        CV,
        pytest.param(
            FCV,
            marks=pytest.mark.xfail(
                raises=System.NotImplementedException,
                reason='Mapping FastCyclicVoltammetry between the legacy method and the domain is not supported yet.',
            ),
        ),
        LSV,
        LSV_aux,
        pytest.param(
            ACV,
            marks=pytest.mark.skip(
                reason='Hangs on System.Text.Json.JsonException: The JSON value could not be converted to System.Double.'
            ),
        ),
        SWV,
        pytest.param(
            CP,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        pytest.param(
            SCP,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        pytest.param(
            LSP,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        pytest.param(
            OCP,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        CA,
        FAM,
        DPV,
        PAD,
        pytest.param(
            MPAD,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        NPV,
        MA,
        pytest.param(
            MP,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        CC,
        pytest.param(
            EIS,
            marks=pytest.mark.xfail(
                raises=System.Net.Http.HttpRequestException,
                reason='ES4LR20B0008 returned error code 405',
            ),
        ),
        pytest.param(
            EIS_pot_fixed,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            EIS_pot_scan,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            EIS_time_scan,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            EIS_time_fixed,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            EIS_single_point,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            FIS,
            marks=pytest.mark.xfail(
                raises=System.ArgumentOutOfRangeException,
                reason='Specified argument was out of the range of valid values. (Parameter `legacyTechnique`)',
            ),
        ),
        pytest.param(
            GIS_cur_fixed,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            GIS_cur_scan,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            GIS_time_scan,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            GIS_time_fixed,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            GIS_single_point,
            marks=pytest.mark.xfail(
                raises=System.ArgumentNullException,
                reason='Value cannot be null. (Parameter `method.ToMethodParameters()`)',
            ),
        ),
        pytest.param(
            FGIS,
            marks=pytest.mark.xfail(
                raises=System.ArgumentOutOfRangeException,
                reason='Specified argument was out of the range of valid values. (Parameter `legacyTechnique`)',
            ),
        ),
        pytest.param(
            MS,
            marks=pytest.mark.skip(
                reason='Hangs on System.Text.Json.JsonException: The JSON value could not be converted to System.Double.'
            ),
        ),
        pytest.param(
            MM,
            marks=pytest.mark.xfail(
                raises=System.NotImplementedException,
                reason='Unknown stage type: MixedModeStageEIS',
            ),
        ),
    ),
)
async def test_lablink_measurements(session, method):
    params = BaseTechnique._registry[method.id].from_dict(method.kwargs)

    [instrument] = session.instruments
    async with await session.claim(instrument) as claim:
        job = await session.start(claim, method=params)
        measurement = await job
    assert measurement
