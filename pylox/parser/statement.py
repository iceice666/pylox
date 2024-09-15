from typing import Optional

from rusty_utils import Catch

from pylox.ast.expression import IExpr, Identifier
from pylox.ast.statement import Program, IStmt, PrintStmt, ExprStmt, VarDecl, Assignment
from pylox.lexer.tokens import TokenType
from pylox.parser.error import ParseError, ErrorKinds
from pylox.parser.expression import expression
from pylox.parser.source import Source


@Catch(ParseError)  # type: ignore
def assignment(source: Source) -> IStmt:
    expr = expression(source).unwrap_or_raise()
    if source.match(TokenType.SEMICOLON):
        return ExprStmt(expr)

    if source.match(TokenType.EQUAL):
        value = expression(source).unwrap_or_raise()
        if isinstance(expr, Identifier):

            if source.match(TokenType.SEMICOLON):
                return Assignment(expr.name, value)

            raise ParseError(
                ErrorKinds.EXPECTED_TOKEN,
                source,
                TokenType.SEMICOLON,
            )

        raise ParseError(
            ErrorKinds.UNEXPECTED_TOKEN,
            source,
            TokenType.IDENTIFIER,
        )

    raise ParseError(
        ErrorKinds.EXPECTED_TOKEN,
        source,
        TokenType.SEMICOLON,
    )


@Catch(ParseError)  # type: ignore
def print_statement(source: Source) -> IStmt:
    expr = expression(source).unwrap_or_raise()
    if source.match(TokenType.SEMICOLON):
        return PrintStmt(expr)

    raise ParseError(
        ErrorKinds.EXPECTED_TOKEN,
        source,
        TokenType.SEMICOLON,
    )


@Catch(ParseError)  # type: ignore
def statement(source: Source) -> IStmt:
    res: IStmt
    if source.match(TokenType.PRINT):
        res = print_statement(source).unwrap_or_raise()
    else:
        res = assignment(source).unwrap_or_raise()

    return res


@Catch(ParseError)  # type: ignore
def variable_declaration(source: Source) -> IStmt:
    if source.match(TokenType.IDENTIFIER):
        name = str(source.prev().unwrap_or_raise().value)
        expr: Optional[IExpr] = None

        if source.match(TokenType.EQUAL):
            expr = expression(source).unwrap_or_raise()

        if source.match(TokenType.SEMICOLON):
            return VarDecl(name, expr)

        raise ParseError(
            ErrorKinds.EXPECTED_TOKEN,
            source,
            TokenType.SEMICOLON,
        )

    raise ParseError(
        ErrorKinds.EXPECTED_TOKEN,
        source,
        TokenType.IDENTIFIER,
    )


@Catch(ParseError)  # type: ignore
def declaration(source: Source) -> IStmt:
    res: IStmt
    if source.match(TokenType.VAR):
        res = variable_declaration(source).unwrap_or_raise()
    else:
        res = statement(source).unwrap_or_raise()

    return res


@Catch(ParseError)  # type: ignore
def program(source: Source) -> Program:
    statements = []
    while source.has_next():
        statements.append(declaration(source).unwrap_or_raise())
    return Program(statements)
