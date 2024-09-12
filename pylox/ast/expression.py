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

from rusty_utils import Result, Ok, Err

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseError, ParseErrorKinds
from pylox.parser.source import Source


class IExpr(abc.ABC):
    pass


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


def primary(source: Source) -> Result[IExpr, ParseError]:
    if source.match(TokenType.NUMBER, TokenType.STRING):
        return Ok(Literal(source.prev().unwrap_or_raise().value))

    if source.match(TokenType.TRUE):
        return Ok(Literal(True))

    if source.match(TokenType.FALSE):
        return Ok(Literal(False))

    if source.match(TokenType.NIL):
        return Ok(Literal(None))

    if source.match(TokenType.LEFT_PAREN):
        expr: IExpr = expression(source).unwrap_or_raise()

        if not source.match(TokenType.RIGHT_PAREN):
            raise ParseError(ParseErrorKinds.EXPECTED_TOKEN, source, TokenType.RIGHT_PAREN)

        return Ok(Grouping(expr))

    return Err(ParseError(ParseErrorKinds.UNREACHABLE))


def unary(source: Source) -> Result[IExpr, ParseError]:
    if source.match(TokenType.BANG, TokenType.MINUS):
        match (source.prev(), unary(source)):
            case (Ok(operator), Ok(right)):
                return Ok(Unary(operator, right))
            case (err1, err2):
                return err1.and_(err2)

    return primary(source)


def factor(source: Source) -> Result[IExpr, ParseError]:
    expr: IExpr = unary(source).unwrap_or_raise()

    while source.match(TokenType.SLASH, TokenType.STAR):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = unary(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return Ok(expr)


def term(source: Source) -> Result[IExpr, ParseError]:
    expr: IExpr = factor(source).unwrap_or_raise()

    while source.match(TokenType.MINUS, TokenType.PLUS):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = factor(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return Ok(expr)


def comparison(source: Source) -> Result[IExpr, ParseError]:
    expr: IExpr = term(source).unwrap_or_raise()

    while source.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = term(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return Ok(expr)


def equality(source: Source) -> Result[IExpr, ParseError]:
    expr: IExpr = comparison(source).unwrap_or_raise()

    while source.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = comparison(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return Ok(expr)


def expression(source: Source) -> Result[IExpr, ParseError]:
    return Ok(equality(source).unwrap_or_raise())


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
