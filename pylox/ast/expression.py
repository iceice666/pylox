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
import enum
from dataclasses import dataclass

from rusty_utils import Catch

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseError, ParseErrorKinds
from pylox.parser.source import Source


class IExpr:
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
    value: object


@dataclass
class Grouping(IExpr):
    expression: IExpr


@Catch(ParseError)  # type: ignore
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

    raise ParseError(ParseErrorKinds.EXPECTED_TOKEN, source,
                     TokenType.NUMBER,
                     TokenType.STRING,
                     TokenType.TRUE,
                     TokenType.FALSE,
                     TokenType.NIL,
                     TokenType.LEFT_PAREN)


@Catch(ParseError)  # type: ignore
def unary(source: Source) -> IExpr:
    if source.match(TokenType.BANG, TokenType.MINUS):
        operator: Token = source.prev().unwrap_or_raise()
        right: IExpr = unary(source).unwrap_or_raise()
        return Unary(operator, right)

    primary_expr: IExpr = primary(source).unwrap_or_raise()
    return primary_expr


@Catch(ParseError)  # type: ignore
def factor(source: Source) -> IExpr:
    expr: IExpr = unary(source).unwrap_or_raise()

    while source.match(TokenType.SLASH, TokenType.STAR):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = unary(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)  # type: ignore
def term(source: Source) -> IExpr:
    expr: IExpr = factor(source).unwrap_or_raise()

    while source.match(TokenType.MINUS, TokenType.PLUS):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = factor(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)  # type: ignore
def comparison(source: Source) -> IExpr:
    expr: IExpr = term(source).unwrap_or_raise()

    while source.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = term(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)  # type: ignore
def equality(source: Source) -> IExpr:
    expr: IExpr = comparison(source).unwrap_or_raise()

    while source.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
        operator: BinaryOp = BinaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = comparison(source).unwrap_or_raise()
        expr = Binary(expr, operator, right)

    return expr


@Catch(ParseError)  # type: ignore
def expression(source: Source) -> IExpr:
    expr: IExpr = equality(source).unwrap_or_raise()
    return expr


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
