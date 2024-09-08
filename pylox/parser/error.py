from enum import Enum
from typing import Optional, TypeVar, TypeAlias, TYPE_CHECKING

from rusty_utils import Result

if TYPE_CHECKING:
    from pylox.lexer.tokens import TokenType
    from pylox.parser.source import Source


class ParseErrorKinds(Enum):
    UNREACHABLE = "Unreachable"
    UNEXPECTED_TOKEN = "Unexpected token"
    UNEXPECTED_EOF = "Unexpected end of file"
    EXPECTED_TOKEN = "Expected token"


class ParseError(Exception):
    def __init__(self, kind: ParseErrorKinds, source: Optional["Source"] = None, tt: Optional["TokenType"] = None):
        self.kind = kind
        self.source = source
        self.tt = tt

    def __str__(self) -> str:
        return f"{self.kind.value} @ {self.source} ({self.tt})"


_T = TypeVar('_T', covariant=True)
ParseResult: TypeAlias = Result[_T, ParseError]
