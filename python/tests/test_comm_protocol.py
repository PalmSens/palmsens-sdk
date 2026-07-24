from __future__ import annotations

import logging

import pytest

import pypalmsens as ps
from pypalmsens._instruments.comm_protocol import CommProtocolError

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def comm():
    instruments = ps.discover()
    with ps.CommProtocol(instruments[0]) as comm_protocol:
        logger.warning('Connected to %s' % comm_protocol.instrument.id)
        yield comm_protocol


@pytest.mark.instrument
@pytest.mark.parametrize(
    'q',
    ('', '\n', 't', 'i', 'v', 'CC', 'CM'),
)
def test_query(comm, q):
    ret = comm.query(q)

    if q in ('', '\n'):
        assert ret == ''
    else:
        assert ret


@pytest.mark.instrument
def test_run_methodscript(comm):
    script = 'send_string "hello world!"'

    ret = comm.run_methodscript(script)
    assert ret == 'Thello world!\n'


@pytest.mark.instrument
def test_run_methodscript_fail(comm):
    script = 'fail!'

    with pytest.raises(CommProtocolError):
        _ = comm.run_methodscript(script)


@pytest.mark.instrument
def test_get_methodscript_capabilities(comm):
    ret = comm.get_methodscript_capabilities()
    assert 'var' in ret


@pytest.mark.instrument
def test_get_communication_capabilities(comm):
    ret = comm.get_communication_capabilities()
    assert 't' in ret


@pytest.mark.instrument
def test_flush(comm):
    comm.write('t')
    ret = comm.flush()
    assert ret.endswith('*\n')


@pytest.mark.instrument
def test_abort_nothing(comm):
    comm.abort()


@pytest.mark.instrument
@pytest.mark.parametrize(
    'q, error_code',
    (
        ('fail', '0003'),
        ('Z', '0006'),
        ('e\nfail\n\n', '4001'),
    ),
)
def test_error(comm, q, error_code):
    with pytest.raises(CommProtocolError) as e:
        comm.query(q)
        assert e.error_code == error_code
