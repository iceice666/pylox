from enum import Enum
from typing import TypeVar, Optional

from rusty_utils import Result

from src.lexer.source import Source

class LexicalErrorKinds(Enum):
    IO_ERROR = "I/O Error"
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
    kind: LexicalErrorKinds

    def __init__(self, kind: LexicalErrorKinds, source: Optional[Source] = None, char: str = ''):
        super().__init__()
        self.kind = kind
        self.source = source
        self.char = char

    def __str__(self, source: Optional[Source] = None, char: str = ''):
        return f"{self.kind.value}\nAt {self.source.current if self.source else 'unknown source'}"


_T = TypeVar('_T', covariant=True)
LexerResult = Result[_T, LexicalError]
