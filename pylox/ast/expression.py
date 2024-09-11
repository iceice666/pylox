"""
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
import enum
from dataclasses import dataclass
from typing import TypeVar, Generic

from rusty_utils import Catch

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseError, ParseErrorKinds
from pylox.parser.source import Source


class IExpr(abc.ABC):
    pass


ResolverT = TypeVar("ResolverT")
ResolverContextT = TypeVar("ResolverContextT")


class UnaryOp(enum.Enum):
    NOT = "!"
    NEG = "-"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_token(token: Token) -> "UnaryOp":
        match token.type:
            case TokenType.BANG:
                return UnaryOp.NOT
            case TokenType.MINUS:
                return UnaryOp.NEG
            case _:
                raise ParseError(ParseErrorKinds.UNEXPECTED_TOKEN, tt=token.type)


@dataclass
class Unary(IExpr):
    operator: Token
    right: IExpr


class BinaryOp(enum.Enum):
    DIV = "/"
    MUL = "*"
    SUB = "-"
    ADD = "+"
    MOD = "%"
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    NE = "!="
    EQ = "=="

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_token(token: Token) -> "BinaryOp":
        match token.type:
            case TokenType.SLASH:
                return BinaryOp.DIV
            case TokenType.STAR:
                return BinaryOp.MUL
            case TokenType.MINUS:
                return BinaryOp.SUB
            case TokenType.PLUS:
                return BinaryOp.ADD
            case TokenType.GREATER:
                return BinaryOp.GT
            case TokenType.GREATER_EQUAL:
                return BinaryOp.GTE
            case TokenType.LESS:
                return BinaryOp.LT
            case TokenType.LESS_EQUAL:
                return BinaryOp.LTE
            case TokenType.BANG_EQUAL:
                return BinaryOp.NE
            case TokenType.EQUAL_EQUAL:
                return BinaryOp.EQ
            case _:
                raise ParseError(ParseErrorKinds.UNEXPECTED_TOKEN, tt=token.type)


@dataclass
class Binary(IExpr):
    left: IExpr
    operator: BinaryOp
    right: IExpr


@dataclass
class Literal(IExpr):
    value: str | int | float | bool | None


@dataclass
class Grouping(IExpr):
    expression: IExpr


class IExprResolver(abc.ABC, Generic[ResolverT, ResolverContextT]):
    @abc.abstractmethod
    def resolve_literal(self, context: ResolverContextT, value: Literal) -> ResolverT: ...

    @abc.abstractmethod
    def resolve_grouping(self, context: ResolverContextT, value: Grouping) -> ResolverT: ...

    @abc.abstractmethod
    def resolve_unary(self, context: ResolverContextT, value: Unary) -> ResolverT: ...

    @abc.abstractmethod
    def resolve_binary(self, context: ResolverContextT, value: Binary) -> ResolverT: ...


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
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = unary(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def term(source: Source) -> IExpr:
    expr: IExpr = factor(source).unwrap_or_raise()

    while source.match(TokenType.MINUS, TokenType.PLUS):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = factor(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def comparison(source: Source) -> IExpr:
    expr: IExpr = term(source).unwrap_or_raise()

    while source.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = term(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)
def equality(source: Source) -> IExpr:
    expr: IExpr = comparison(source).unwrap_or_raise()

    while source.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
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
