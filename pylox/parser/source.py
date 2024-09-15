from typing import List

from rusty_utils import Option, Catch

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseResult, ParseError, ParseErrorKinds


class Source:
    current = 0

    def __init__(self, tokens: List[Token]):
        self.__tokens = tokens

    def advance(self) -> Option[Token]:
        if self.has_next():
            tk = self.__tokens[self.current]
            self.current += 1
            return Option(tk)
        return Option()

    def peek(self) -> Option[Token]:
        return Option(self.__tokens[self.current] if self.has_next() else None)

    def prev(self) -> ParseResult[Token]:
        return (
            Catch(IndexError)(lambda: self.__tokens[self.current - 1])()
            .map_err(lambda _: ParseError(ParseErrorKinds.EXPECTED_TOKEN))
        )

    def check(self, *token_type: TokenType) -> bool:
        """Checks if the next token is any of the given types."""
        # Explict type cast here to satisfy mypy
        return bool(self.peek().is_some_and(lambda t: t.type in token_type))

    def consume(self) -> ParseResult[None]:
        return self.advance().ok_or(ParseError(ParseErrorKinds.UNEXPECTED_TOKEN, source=self))

    def has_next(self) -> bool:
        return self.current < len(self.__tokens)

    def match(self, *expected: TokenType) -> bool:
        """Consumes the next token if it matches any of the expected types."""
        for ty in expected:
            if self.check(ty):
                self.advance()
                return True
        return False
