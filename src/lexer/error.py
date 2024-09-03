from enum import Enum
from typing import TypeVar

from result import Ok, Err

from src.lexer.source import Source


class LexicalErrorKinds(Enum):
    IO_ERROR = "I/O Error"
    UNEXPECTED_CHARACTER = "Unexpected character"
    UNTERMINATED_STRING_LITERAL = "Unterminated string literal"
    UNTERMINATED_CHAR_LITERAL = "Unterminated char literal"
    EMPTY_CHAR_DECLARATION = "Empty character declaration"
    INVALID_ESCAPE_SEQUENCE = "Invalid escape sequence"
    MALFORMED_NUMBER = "Invalid number literal"
    HOW_DID_YOU_GET_HERE = "How you supposed to get here"
    NOP = "No operation"
    EOF = "Reached end of file"


class LexicalError(Exception):
    """Base class for lexical errors."""

    source: Source
    char: str
    kind: LexicalErrorKinds

    def __init__(self, source: Source = None, char: str = ''):
        super().__init__()
        self.source = source
        self.char = char

    def bind(self, kind: LexicalErrorKinds):
        self.kind = kind
        return self

    def __str__(self, source: Source = None, char: str = ''):
        match self:
            case LexicalErrorKinds.IO_ERROR:
                return f"{LexicalErrorKinds.IO_ERROR.value}: {char}"
            case LexicalErrorKinds.UNEXPECTED_CHARACTER:
                return f"{LexicalErrorKinds.UNEXPECTED_CHARACTER.value} at {source}: '{char}'"
            case LexicalErrorKinds.UNTERMINATED_STRING_LITERAL:
                return f"{LexicalErrorKinds.UNTERMINATED_STRING_LITERAL.value} at {source}"
            case LexicalErrorKinds.UNTERMINATED_CHAR_LITERAL:
                return f"{LexicalErrorKinds.UNTERMINATED_CHAR_LITERAL.value} at {source}"
            case LexicalErrorKinds.EMPTY_CHAR_DECLARATION:
                return f"{LexicalErrorKinds.EMPTY_CHAR_DECLARATION.value} at {source}"
            case LexicalErrorKinds.INVALID_ESCAPE_SEQUENCE:
                return f"{LexicalErrorKinds.INVALID_ESCAPE_SEQUENCE.value} at {source}: '{char}'"
            case LexicalErrorKinds.MALFORMED_NUMBER:
                return f"{LexicalErrorKinds.MALFORMED_NUMBER.value} at {source}"
            case LexicalErrorKinds.HOW_DID_YOU_GET_HERE:
                return f"{LexicalErrorKinds.HOW_DID_YOU_GET_HERE.value} at {source}"
            case LexicalErrorKinds.NOP:
                return LexicalErrorKinds.NOP.value
            case LexicalErrorKinds.EOF:
                return f"{LexicalErrorKinds.EOF.value} at {source}"
            case _:
                return "Unknown error"


_T = TypeVar('_T', covariant=True)
LexerResult = Ok[_T] | Err[LexicalError]
