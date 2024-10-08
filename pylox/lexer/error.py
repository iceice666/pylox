from enum import Enum
from typing import TypeVar, Optional

from rusty_utils import Result

from pylox.lexer.source import Source

class ErrorKinds(Enum):
    UNEXPECTED_CHARACTER = "Unexpected character"
    UNTERMINATED_STRING_LITERAL = "Unterminated string literal"
    UNTERMINATED_CHAR_LITERAL = "Unterminated char literal"
    EMPTY_CHAR_DECLARATION = "Empty character declaration"
    INVALID_ESCAPE_SEQUENCE = "Invalid escape sequence"
    MALFORMED_NUMBER = "Invalid number literal"
    HOW_DID_YOU_GET_HERE = "How you supposed to get here???"
    NOP = "No operation"
    EOF = "Reached end of file"


class LexicalError(Exception):
    """Base class for lexical errors."""

    source: Optional[Source]
    char: str
    kind: ErrorKinds

    def __init__(self, kind: ErrorKinds, source: Optional[Source] = None, char: str = ''):
        super().__init__()
        self.kind = kind
        self.source = source
        self.char = char

    def __str__(self) -> str:
        return f"{self.kind.value} @ {self.source.current if self.source else 'unknown source'}"


_T = TypeVar('_T', covariant=True)
LexerResult = Result[_T, LexicalError]
