from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

docs_dir = Path(__file__).parent / 'zensical'


GROUP_MODULES: dict[str, dict[str, Any]] = defaultdict(dict)


# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'data.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'measuring.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'methods.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'index.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'filesystem.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'files.md')), ids=str)
# @pytest.mark.parametrize('example', list(find_examples(docs_dir / 'comm_protocol.md')), ids=str)
# @pytest.mark.parametrize(
#     'example', list(find_examples(docs_dir / 'circuit_fitting.md')), ids=str
# )
@pytest.mark.parametrize('example', list(find_examples(docs_dir / 'events.md')), ids=str)
def test_docstrings(example: CodeExample, eval_example: EvalExample):
    eval_example.set_config(
        ruff_ignore=['D', 'T', 'B', 'C4', 'F821', 'E721', 'Q001', 'PERF', 'PIE790'],
        line_length=88,
        target_version='py310',
    )

    settings = example.prefix_settings()
    group = example.path.name

    d = GROUP_MODULES[group]

    eval_example.set_config(target_version='py310')

    eval_example.format_black(example)

    if settings.get('test') != 'skip':
        module_dict = eval_example.run_print_update(example, module_globals=d)

        GROUP_MODULES[group] = module_dict
