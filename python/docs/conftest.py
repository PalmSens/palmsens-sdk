from __future__ import annotations

import doctest
from os import chdir, getcwd
from shutil import rmtree
from tempfile import mkdtemp

import pytest
from sybil import Sybil
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.markdown import PythonCodeBlockParser


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


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=doctest.ELLIPSIS),
        PythonCodeBlockParser(future_imports=['print_function']),
    ],
    pattern='comm_protocol.md',
    fixtures=['tempdir'],
).pytest()
