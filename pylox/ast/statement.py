"""
program        → statement* EOF ;

declaration    → varDecl
               | statement ;

statement      → assignStmt
               | printStmt
               | block ;

assignStmt     → assignment | exprStmt ;


block          → "{" declaration* "}" ;
varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
assignment     → IDENTIFIER "=" expression ";" ;
exprStmt       → expression ";" ;
printStmt      → "print" expression ";" ;
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
class PrintStmt(IStmt):
    expr: IExpr


@dataclass
class Assignment(IStmt):
    name: str
    value: IExpr

@dataclass
class Block(IStmt):
    statements: list[IStmt]


Statement: TypeAlias = ExprStmt | PrintStmt | Assignment | Block


@dataclass
class VarDecl(IStmt):
    name: str
    init: Optional[IExpr]


Declaration: TypeAlias = Union[VarDecl, Statement]


@dataclass
class Program(IStmt):
    statements: list[Statement]
