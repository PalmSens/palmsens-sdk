from __future__ import annotations

from pathlib import Path

import pytest

import pypalmsens as ps
from pypalmsens._methodscript import validate as validate_methodscript

SAMPLES_DIR = Path(__file__).parent / 'samples'
SAMPLES = [pytest.param(path, id=path.stem) for path in SAMPLES_DIR.glob('*.mscr')]


def test_remove_leading_e():
    script = 'e\ncell_on\n'
    method = ps.MethodScript(script=script)

    assert method.script == 'cell_on\n'


def test_remove_trailing_newlines():
    script = 'cell_on\n\n'
    method = ps.MethodScript(script=script)

    assert method.script == 'cell_on\n'


def test_add_newlines():
    script = 'cell_on'
    method = ps.MethodScript(script=script)

    assert method.script == 'cell_on\n'


@pytest.mark.parametrize('path', SAMPLES)
def test_validate_samples(path):
    expect_success = path.name.startswith('valid')
    expect_failure = path.name.startswith('error')

    text = path.read_text()

    try:
        validate_methodscript(text)
    except SyntaxError:
        assert expect_failure
    else:
        assert expect_success
