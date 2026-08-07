from __future__ import annotations

import doctest
from os import chdir, getcwd
from shutil import rmtree
from tempfile import mkdtemp

import pytest
from sybil import Example, Sybil
from sybil.evaluators.doctest import NUMBER
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.markdown import CodeBlockParser, PythonCodeBlockParser, SkipParser


@pytest.fixture(scope='module')
def tempdir():
    # there are better ways to do temp directories, but it's a simple example:
    path = mkdtemp()
    cwd = getcwd()
    try:
        chdir(path)
        yield path
    finally:
        chdir(cwd)
        rmtree(path)


def lint_python_source(example: Example) -> str | None:
    # here you'd feed example.parsed, which contains the python source of the
    # .. code-block:: python, to your linting tool of choice
    pass


linting = Sybil(
    name='linting',
    parsers=[
        CodeBlockParser(language='python', evaluator=lint_python_source),
    ],
    patterns=['*.md'],
)

testing = Sybil(
    parsers=[
        DocTestParser(
            optionflags=doctest.ELLIPSIS
            | doctest.NORMALIZE_WHITESPACE
            | doctest.IGNORE_EXCEPTION_DETAIL
        ),
        PythonCodeBlockParser(
            doctest_optionflags=NUMBER,
        ),
        SkipParser(),
    ],
    patterns=[
        'comm_protocol.md',
        'circuit_fitting.md',
        'data.md',
        'events.md',
        'examples.md',
        'files.md',
        'filesystem.md',
        'installation.md',
        'index.md',
        'measuring.md',
        'methods.md',
    ],
    excludes=['zensical/releases/index.md'],
)


pytest_collect_file = testing.pytest()
