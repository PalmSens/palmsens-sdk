from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

docs_dir = Path(__file__).parent / 'zensical'


GROUP_MODULES: dict[str, dict[str, Any]] = defaultdict(dict)


# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'data.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'docs.md')), ids=str)
@pytest.mark.parametrize('example', list(find_examples(docs_dir / 'measuring.md')), ids=str)
def test_docstrings(example: CodeExample, eval_example: EvalExample):
    settings = example.prefix_settings()

    group = example.path.name

    d = GROUP_MODULES[group]

    eval_example.set_config(target_version='py310')

    if settings.get('test') == 'skip':
        return

    module_dict = eval_example.run_print_update(example, module_globals=d)

    GROUP_MODULES[group] = module_dict
