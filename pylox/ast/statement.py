"""
program        → statement* EOF ;

declaration    → varDecl
               | statement ;

statement      → assignStmt
               | ifStmt
               | whileStmt
               | forStmt
               | block ;

assignStmt     → assignment | exprStmt ;

ifStmt         → "if" "(" expression ")" statement
               ( "else" statement )? ;
whileStmt      → "while" "(" expression ")" statement ;
forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                 expression? ";"
                 expression? ")" statement ;

block          → "{" declaration* "}" ;
varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
assignment     → IDENTIFIER "=" expression ";" ;
exprStmt       → expression ";" ;
"""
from dataclasses import dataclass
from typing import Union, TypeAlias, Optional

from pylox.ast.expression import IExpr


class IStmt:
    pass


@dataclass
class ExprStmt(IStmt):
    expr: IExpr


@dataclass
class Assignment(IStmt):
    name: str
    value: IExpr


@dataclass
class Block(IStmt):
    statements: list[IStmt]


@dataclass
class IfStmt(IStmt):
    condition: IExpr
    then_branch: IStmt
    else_branch: Optional[IStmt]


@dataclass
class WhileStmt(IStmt):
    condition: IExpr
    body: IStmt


Statement: TypeAlias = ExprStmt  | Assignment | Block | IfStmt


@dataclass
class VarDecl(IStmt):
    name: str
    init: Optional[IExpr]


Declaration: TypeAlias = Union[VarDecl, Statement]


@dataclass
class Program(IStmt):
    statements: list[Statement]
