from __future__ import annotations

import pytest
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from typing_extensions import override

from pypalmsens._methodscript import (
    MethodScriptLexer,
    MethodScriptParser,
)

PASSING_TESTS = [
    pytest.param(
        'var voltage\n',
        id='Simple variable declaration',
    ),
    pytest.param(
        'beep 1i 5i 100m\n',
        id='Simple command',
    ),
    pytest.param(
        'set_e 500m # Set potential\n',
        id='Command with comment',
    ),
    pytest.param(
        'array data 10i\n',
        id='Array declaration',
    ),
    pytest.param(
        'if voltage > 100m\n    cell_on\nendif\n',
        id='If statement',
    ),
    pytest.param(
        'var count\nif count == -3i\n    beep 1i 1i 1m\nendif\n',
        id='If statement with negative integer literal',
    ),
    pytest.param(
        'str s\nstore_str s "Price: \u20ac10"\n',
        id='Non-ASCII in string literal',
    ),
    pytest.param(
        'cell_on\nvar var1\nstore_var var1 "\U0001f600" aa\n',
        id='Emoji in string literal',
    ),
    pytest.param(
        'var current\nmeas_loop_ca current 0m 1m 10m\n    copy_var current cr\nendloop\n',
        id='Measurement loop',
    ),
    pytest.param(
        'cell_on\n',
        id='One trailing newline',
    ),
]


FAILING_TESTS = [
    pytest.param(
        '# Comment with \u20ac symbol\n',
        id='Non-ASCII in comment',
    ),
    pytest.param(
        'cell_on\nvar var1\nstore_var var1 \U0001f600 aa\n', id='Emoji unquoted (lexer error)'
    ),
    pytest.param(
        'e\ncell_on\n',
        id='Starts with e',
    ),
    pytest.param(
        'cell_on\n\ncell_off\n',
        id='Contains newline',
    ),
    pytest.param(
        'cell_on',
        id='No trailing newlines',
    ),
    pytest.param(
        'cell_on\n\n',
        id='Multiple trailing newlines',
    ),
]


class RaisingErrorListener(ErrorListener):
    """Error listener that raises on syntax errors."""

    @override
    def syntaxError(self, recognizer, offendingSymbol, line: int, column: int, msg: str, e):
        """Raise on error."""
        raise SyntaxError(msg)


def setup_parser(script: str):
    chars = InputStream(script)
    lexer = MethodScriptLexer(chars)
    tokens = CommonTokenStream(lexer)
    parser = MethodScriptParser(tokens)

    error_listener = RaisingErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    return parser


@pytest.mark.parametrize('script', PASSING_TESTS)
def test_parse_input(script: str):
    """Parse MethodScript source and return the tree plus collected errors."""
    parser = setup_parser(script)

    tree = parser.sourceFile()

    assert tree


@pytest.mark.parametrize('script', FAILING_TESTS)
def test_parse_input_fail(script: str):
    """Parse MethodScript source and return the tree plus collected errors."""
    parser = setup_parser(script)

    with pytest.raises(SyntaxError):
        _ = parser.sourceFile()
