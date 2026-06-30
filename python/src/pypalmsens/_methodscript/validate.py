from __future__ import annotations

from dataclasses import dataclass

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from .generated.MethodScriptLexer import MethodScriptLexer
from .generated.MethodScriptParser import MethodScriptParser


@dataclass
class MethodScriptError:
    text: str
    line: int
    column: int

    @property
    def message(self) -> str:
        return f'line {self.line}:{self.column}: {self.text}'


class CollectingErrorListener(ErrorListener):
    """Error listener that records syntax errors instead of printing them."""

    def __init__(self):
        super().__init__()
        self.errors: list[MethodScriptError] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(MethodScriptError(line=line, column=column, text=msg))


def validate(text: str) -> None:
    """Parse MethodScript source and return the list of syntax errors.

    Parameters
    ----------
    text: str
        Input text to validate.

    Raises
    ------
    SyntaxError
        If the text cannot be parsed.
    """
    chars = InputStream(text)
    lexer = MethodScriptLexer(chars)

    lexer_listener = CollectingErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_listener)

    tokens = CommonTokenStream(lexer)
    parser = MethodScriptParser(tokens)

    parser_listener = CollectingErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(parser_listener)

    _ = parser.sourceFile()

    errors = lexer_listener.errors + parser_listener.errors

    if errors:
        raise SyntaxError('\n'.join(error.message for error in errors))
