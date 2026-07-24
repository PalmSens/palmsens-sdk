from __future__ import annotations

import asyncio
import logging

import pytest
import pytest_asyncio

import pypalmsens as ps
from pypalmsens._instruments.comm_protocol import CommProtocolError

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope='module')
async def comm():
    instruments = await ps.discover_async()
    async with ps.CommProtocolAsync(instruments[0]) as comm_protocol:
        logger.warning('Connected to %s' % comm_protocol.instrument.id)
        yield comm_protocol


@pytest.mark.asyncio
@pytest.mark.instrument
@pytest.mark.parametrize(
    'q',
    ('', '\n', 't', 'i', 'v', 'CC', 'CM'),
)
async def test_query(comm, q):
    ret = await comm.query(q)

    if q in ('', '\n'):
        assert ret == ''
    else:
        assert ret


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_run_methodscript(comm):
    script = 'send_string "hello world!"'

    ret = await comm.run_methodscript(script)
    assert ret == 'Thello world!\n'


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_run_methodscript_fail(comm):
    script = 'fail!'

    with pytest.raises(CommProtocolError):
        _ = await comm.run_methodscript(script)


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_get_methodscript_capabilities(comm):
    ret = await comm.get_methodscript_capabilities()
    assert 'var' in ret


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_get_communication_capabilities(comm):
    ret = await comm.get_communication_capabilities()
    assert 't' in ret


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_flush(comm):
    await comm.write('t')
    await asyncio.sleep(0.1)
    ret = await comm.flush()
    assert ret.endswith('*\n')


@pytest.mark.asyncio
@pytest.mark.instrument
async def test_abort_nothing(comm):
    await comm.abort()


@pytest.mark.asyncio
@pytest.mark.instrument
@pytest.mark.parametrize(
    'q, error_code',
    (
        ('fail', '0003'),
        ('Z', '0006'),
        ('e\nfail\n\n', '4001'),
    ),
)
async def test_error(comm, q, error_code):
    with pytest.raises(CommProtocolError) as e:
        _ = await comm.query(q)
        assert e.error_code == error_code
