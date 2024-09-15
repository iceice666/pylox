"""
program        → statement* EOF ;

declaration    → varDecl
               | statement ;

varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
assignment     → IDENTIFIER "=" expression ";" ;

statement      → assignStmt
               | printStmt ;

assignStmt     → assignment | exprStmt ;

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


Statement: TypeAlias = ExprStmt | PrintStmt | Assignment


@dataclass
class VarDecl(IStmt):
    name: str
    init: Optional[IExpr]


Declaration: TypeAlias = Union[VarDecl, Statement]


@dataclass
class Program(IStmt):
    statements: list[Statement]
