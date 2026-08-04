from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

docs_dir = Path(__file__).parent / 'zensical'


MODULE_GLOBALS: dict[str, Any] = {}


@pytest.mark.parametrize('example', list(find_examples(docs_dir / 'data.md')), ids=str)
def test_docstrings(example: CodeExample, eval_example: EvalExample):
    eval_example.set_config(target_version='py310')

    module_dict = eval_example.run_print_update(example, module_globals=MODULE_GLOBALS)

    MODULE_GLOBALS.update(module_dict)
