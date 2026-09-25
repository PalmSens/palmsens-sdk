import nest_asyncio
import pytest
import pytest_asyncio

from pypalmsens import lablink

nest_asyncio.apply()


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

    data1 = await ref.fetch()
    data2 = await session.fetch_measurement(ref)

    assert ref.guid == data1.guid == data2.guid
