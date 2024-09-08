"""
Grammar for the Lox language.

expression     → equality ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary
               | primary ;
primary        → NUMBER | STRING | "true" | "false" | "nil"
               | "(" expression ")" ;
"""
import abc
from dataclasses import dataclass

from rusty_utils import Catch

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseError, ParseErrorKinds
from pylox.parser.source import Source


class IExpr(abc.ABC):
    pass


@dataclass
class Binary(IExpr):
    left: IExpr
    operator: Token
    right: IExpr


@dataclass
class Literal(IExpr):
    value: str | int | float | bool | None


@dataclass
class Grouping(IExpr):
    expression: IExpr


@dataclass
class Unary(IExpr):
    operator: Token
    right: IExpr


@Catch(ParseError)
def primary(source: Source) -> IExpr:
    if source.match(TokenType.NUMBER, TokenType.STRING):
        return Literal(source.prev().unwrap_or_raise().value)

    if source.match(TokenType.TRUE):
        return Literal(True)

    if source.match(TokenType.FALSE):
        return Literal(False)

    if source.match(TokenType.NIL):
        return Literal(None)

    if source.match(TokenType.LEFT_PAREN):
        expr: IExpr = expression(source).unwrap_or_raise()

        if not source.match(TokenType.RIGHT_PAREN):
            raise ParseError(ParseErrorKinds.EXPECTED_TOKEN, source, TokenType.RIGHT_PAREN)

        return Grouping(expr)

    raise ParseError(ParseErrorKinds.UNREACHABLE)


@Catch(ParseError)
def unary(source: Source) -> IExpr:
    if source.match(TokenType.BANG, TokenType.MINUS):
        operator: Token = source.prev().unwrap_or_raise()
        right: IExpr = unary(source).unwrap_or_raise()
        return Unary(operator, right)

    return primary(source).unwrap_or_raise()


@Catch(ParseError)
def factor(source: Source) -> IExpr:
    expr: IExpr = unary(source).unwrap_or_raise()

    while source.match(TokenType.SLASH, TokenType.STAR):
        operator: Token = source.prev().unwrap_or_raise()
        right: IExpr = unary(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def term(source: Source) -> IExpr:
    expr: IExpr = factor(source).unwrap_or_raise()

    while source.match(TokenType.MINUS, TokenType.PLUS):
        operator: Token = source.prev().unwrap_or_raise()
        right: IExpr = factor(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def comparison(source: Source) -> IExpr:
    expr: IExpr = term(source).unwrap_or_raise()

    while source.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
        operator: Token = source.prev().unwrap_or_raise()
        right: IExpr = term(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def equality(source: Source) -> IExpr:
    expr: IExpr = comparison(source).unwrap_or_raise()

    while source.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
        operator: Token = source.prev().unwrap_or_raise()
        right: IExpr = comparison(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def expression(source: Source) -> IExpr:
    return equality(source).unwrap_or_raise()


def synchronize(source: Source) -> None:
    source.advance()

    while source.has_next():
        if source.prev().unwrap_or_raise().type == TokenType.SEMICOLON:
            return

        if source.check(
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN
        ):
            return

        source.advance()
