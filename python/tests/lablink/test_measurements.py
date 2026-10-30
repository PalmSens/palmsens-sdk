import pytest
import pytest_asyncio

from pypalmsens import lablink

pytest.skip('API not final', allow_module_level=True)


@pytest_asyncio.fixture(scope='module')
async def session():
    session = await lablink.Instance().login('test', 'test')
    return session


@pytest.mark.lablink
@pytest.mark.asyncio
async def test_list_measurements(session: lablink.Session):
    measurements = await session.list_measurements()
    assert measurements

    ref, *_ = measurements

    data1 = await ref.get_data()
    data2 = await session.get_measurement(ref)

    assert ref.guid == data1.guid == data2.guid
