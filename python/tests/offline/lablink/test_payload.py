from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pytest_regressions.data_regression import DataRegressionFixture

from pypalmsens._methods.adapters import technique_adapter
from pypalmsens.lablink.models._method_mapper import (
    to_payload,
)

EXAMPLES_DIR = Path(__file__).parent / 'data'
DATA = [pytest.param(path, id=path.stem) for path in EXAMPLES_DIR.glob('*.yaml')]

if not DATA:
    raise RuntimeError(f'No example YAML files found in {EXAMPLES_DIR}')


@pytest.mark.parametrize('method_file', DATA)
def test_regression(method_file: Path, data_regression: DataRegressionFixture) -> None:
    with open(method_file) as f:
        dct = yaml.safe_load(f)

    method = technique_adapter.validate_python(dct)

    try:
        payload = to_payload(method)
    except NotImplementedError as exc:
        pytest.skip(f'{method_file.stem} is guarded: {exc}')

    data_regression.check(payload)
