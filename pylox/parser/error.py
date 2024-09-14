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
    def __init__(self, kind: ParseErrorKinds, source: Optional["Source"] = None, *tt: "TokenType"):
        self.kind = kind
        self.source = source
        self.tt = tt

    def __str__(self) -> str:
        string = f"Current token is {self.source.peek()}\n{self.kind.value}"
        if self.source:
            string += f" at {self.source.current + 1}th token"
        if self.tt:
            string += f": {', '.join(str(t) for t in self.tt)}"

        return string


_T = TypeVar('_T', covariant=True)
ParseResult: TypeAlias = Result[_T, ParseError]
