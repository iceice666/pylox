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

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseError, ParseErrorKinds


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
    operator: UnaryOp
    right: IExpr


class BinaryOp(enum.Enum):
    DIV = "/"
    MUL = "*"
    SUB = "-"
    ADD = "+"

    GT = ">"
    GE = ">="
    LS = "<"
    LE = "<="
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
                return BinaryOp.GE
            case TokenType.LESS:
                return BinaryOp.LS
            case TokenType.LESS_EQUAL:
                return BinaryOp.LE
            case TokenType.BANG_EQUAL:
                return BinaryOp.NE
            case TokenType.EQUAL_EQUAL:
                return BinaryOp.EQ
            case _:
                raise ParseError(ParseErrorKinds.UNEXPECTED_TOKEN, None, token.type)


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
