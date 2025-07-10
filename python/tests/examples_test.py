import subprocess as sp
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).parents[1]
EXAMPLES = list(ROOT_DIR.glob('*Example*.py'))


@pytest.mark.parametrize('path', EXAMPLES)
@pytest.mark.requires_instrument
def test_examples(path: Path):
    assert path.exists(), f'Missing {path}'

    ret = sp.run([sys.executable, path])

    assert ret.returncode == 0
