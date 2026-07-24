from __future__ import annotations

import logging

import pytest

import pypalmsens as ps

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def comm():
    instruments = ps.discover()
    with ps.CommProtocol(instruments[0]) as comm_protocol:
        logger.warning('Connected to %s' % comm_protocol.instrument.id)
        yield comm_protocol


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


def test_run_methodscript(comm):
    script = 'send_string "hello world!"'

    ret = comm.run_methodscript(script)
    assert ret == 'Thello world!\n'


def test_get_methodscript_capabilities(comm):
    ret = comm.get_methodscript_capabilities()
    assert 'var' in ret


def test_get_communication_capabilities(comm):
    ret = comm.get_communication_capabilities()
    assert 't' in ret


def test_flush(comm):
    comm.write('t')
    ret = comm.flush()
    assert ret.endswith('*\n')


def test_abost(comm):
    comm.abort()
