import subprocess as sp
import sys
from pathlib import Path

import pytest

from pspython.pspyinstruments import discover_instruments

ROOT_DIR = Path(__file__).parents[1]
EXAMPLES = list(ROOT_DIR.glob('*Example*.py'))

requires_instrument = pytest.mark.skipif(
    not discover_instruments(), reason='Needs connected instrument.'
)


@pytest.mark.parametrize('path', EXAMPLES)
@requires_instrument
def test_examples(path: Path):
    assert path.exists(), f'Missing {path}'

    ret = sp.run([sys.executable, path])

    assert ret.returncode == 0
