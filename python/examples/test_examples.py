from __future__ import annotations

import subprocess as sp
import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent
EXAMPLES = [pytest.param(path, id=path.stem) for path in EXAMPLES_DIR.glob('*.py')]


@pytest.mark.parametrize('path', EXAMPLES)
@pytest.mark.examples
def test_examples(path: Path):
    assert path.exists(), f'Missing {path}'

    ret = sp.run([sys.executable, path])

    assert ret.returncode == 0
