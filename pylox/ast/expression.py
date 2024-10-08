"""
expression     → logic_or ;
logic_or       → logic_and ( "or" logic_and )* ;
logic_and      → equality ( "and" equality )* ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary
               | call ;
call           → primary ( "(" arguments? ")" )* ;
arguments      → expression ( "," expression )* ;
primary        → LITERAL
               | "(" expression ")"
               | IDENTIFIER ;
LITERAL        → NUMBER | STRING | "True" | "False" | "None" ;

"""
import enum
from dataclasses import dataclass
from typing import TypeAlias

from pylox.lexer.tokens import Token, TokenType
from pylox.parser.error import ParseError, ErrorKinds


class IExpr:
    pass


@dataclass
class FuncCall(IExpr):
    callee: IExpr
    args: list[IExpr]


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
                raise ParseError(ErrorKinds.UNEXPECTED_TOKEN, tt=token.type)


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
                raise ParseError(ErrorKinds.UNEXPECTED_TOKEN, None, token.type)


@dataclass
class Binary(IExpr):
    left: IExpr
    operator: BinaryOp
    right: IExpr


class LogicalOp(enum.Enum):
    OR = "or"
    AND = "and"

    def __str__(self) -> str:
        return self.value


@dataclass
class Logical(IExpr):
    left: IExpr
    operator: LogicalOp
    right: IExpr


@dataclass
class Literal(IExpr):
    value: object


@dataclass
class Grouping(IExpr):
    expression: IExpr


@dataclass
class Identifier(IExpr):
    name: str


Primary: TypeAlias = Literal | Identifier | Grouping
