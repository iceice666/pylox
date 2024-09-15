from typing import Optional

from rusty_utils import Catch

from pylox.ast.expression import IExpr, Identifier, Literal
from pylox.ast.statement import Program, IStmt, PrintStmt, ExprStmt, VarDecl, Assignment, Block, IfStmt, WhileStmt
from pylox.lexer.tokens import TokenType
from pylox.parser.error import ParseError, ErrorKinds
from pylox.parser.expression import expression
from pylox.parser.source import Source


def parse_expression(source: Source) -> IExpr:
    return expression(source).unwrap_or_raise()


def expect_token(source: Source, token_type: TokenType) -> None:
    if not source.match(token_type):
        raise ParseError(
            ErrorKinds.EXPECTED_TOKEN,
            source,
            token_type,
        )


@Catch(ParseError)  # type: ignore
def assignment(source: Source) -> IStmt:
    expr = parse_expression(source)
    if source.match(TokenType.SEMICOLON):
        return ExprStmt(expr)

    if source.match(TokenType.EQUAL):
        value = parse_expression(source)
        if isinstance(expr, Identifier):
            expect_token(source, TokenType.SEMICOLON)
            return Assignment(expr.name, value)

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
    expr = parse_expression(source)
    expect_token(source, TokenType.SEMICOLON)
    return PrintStmt(expr)


@Catch(ParseError)  # type: ignore
def block(source: Source) -> IStmt:
    statements = []
    while not source.check(TokenType.RIGHT_BRACE) and source.has_next():
        statements.append(declaration(source).unwrap_or_raise())

    expect_token(source, TokenType.RIGHT_BRACE)
    return Block(statements)


@Catch(ParseError)  # type: ignore
def if_statement(source: Source) -> IStmt:
    expect_token(source, TokenType.LEFT_PAREN)
    condition = parse_expression(source)
    expect_token(source, TokenType.RIGHT_PAREN)

    then_branch = statement(source).unwrap_or_raise()
    else_branch: Optional[IStmt] = None

    if source.match(TokenType.ELSE):
        else_branch = statement(source).unwrap_or_raise()

    return IfStmt(condition, then_branch, else_branch)


@Catch(ParseError)  # type: ignore
def statement(source: Source) -> IStmt:
    if source.match(TokenType.PRINT):
        return print_statement(source).unwrap_or_raise()
    if source.match(TokenType.LEFT_BRACE):
        return block(source).unwrap_or_raise()
    if source.match(TokenType.IF):
        return if_statement(source).unwrap_or_raise()
    if source.match(TokenType.WHILE):
        return while_statement(source).unwrap_or_raise()
    if source.match(TokenType.FOR):
        return for_statement(source).unwrap_or_raise()
    return assignment(source).unwrap_or_raise()


@Catch(ParseError)  # type: ignore
def assignment_without_semicolon(source: Source) -> IStmt:
    expr = parse_expression(source)

    if source.match(TokenType.EQUAL):
        value = parse_expression(source)
        if isinstance(expr, Identifier):
            return Assignment(expr.name, value)

    return ExprStmt(expr)


@Catch(ParseError)  # type: ignore
def for_statement(source: Source) -> IStmt:
    expect_token(source, TokenType.LEFT_PAREN)

    init = None
    if not source.match(TokenType.SEMICOLON):
        if source.match(TokenType.VAR):
            init = variable_declaration(source).unwrap_or_raise()
        else:
            init = parse_expression(source)

    condition = None
    if not source.check(TokenType.SEMICOLON):
        condition = parse_expression(source)

    expect_token(source, TokenType.SEMICOLON)

    increment = None
    if not source.check(TokenType.SEMICOLON):
        increment = assignment_without_semicolon(source).unwrap_or_raise()

    expect_token(source, TokenType.RIGHT_PAREN)

    body = statement(source).unwrap_or_raise()

    if increment is not None:
        body = Block([body, increment])

    if condition is None:
        condition = Literal(True)

    body = WhileStmt(condition, body)
    if init is not None:
        body = Block([init, body])

    return body


@Catch(ParseError)  # type: ignore
def while_statement(source: Source) -> IStmt:
    expect_token(source, TokenType.LEFT_PAREN)
    condition = parse_expression(source)
    expect_token(source, TokenType.RIGHT_PAREN)

    body = statement(source).unwrap_or_raise()
    return WhileStmt(condition, body)


@Catch(ParseError)  # type: ignore
def variable_declaration(source: Source) -> IStmt:
    expect_token(source, TokenType.IDENTIFIER)
    name = str(source.prev().unwrap_or_raise().value)
    expr: Optional[IExpr] = None

    if source.match(TokenType.EQUAL):
        expr = parse_expression(source)

    expect_token(source, TokenType.SEMICOLON)
    return VarDecl(name, expr)


@Catch(ParseError)  # type: ignore
def declaration(source: Source) -> IStmt:
    if source.match(TokenType.VAR):
        return variable_declaration(source).unwrap_or_raise()
    return statement(source).unwrap_or_raise()


@Catch(ParseError)  # type: ignore
def program(source: Source) -> Program:
    statements = []
    while source.has_next():
        statements.append(declaration(source).unwrap_or_raise())
    return Program(statements)