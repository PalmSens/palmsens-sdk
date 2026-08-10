from __future__ import annotations

import doctest

from sybil import Sybil
from sybil.evaluators.doctest import NUMBER
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.markdown import PythonCodeBlockParser, SkipParser

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
        '*.md',
    ],
    excludes=[
        'zensical/releases/index.md',
        # comm protocol breaks events.md with INTERNALERROR (?)
        # enable when needed
        'zensical/comm_protocol.md',
    ],
)


pytest_collect_file = testing.pytest()
