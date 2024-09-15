from rusty_utils import Catch

from pylox.ast.expression import IExpr, Literal, Grouping, Unary, BinaryOp, Binary, UnaryOp, Primary, Identifier, \
    LogicalOp, Logical, FuncCall
from pylox.lexer.tokens import TokenType
from pylox.parser.error import ParseError, ErrorKinds
from pylox.parser.source import Source


@Catch(ParseError)  # type: ignore
def primary(source: Source) -> Primary:
    if source.match(TokenType.IDENTIFIER):
        return Identifier(str(source.prev().unwrap_or_raise().value))

    if source.match(TokenType.NUMBER, TokenType.STRING):
        return Literal(source.prev().unwrap_or_raise().value)

    if source.match(TokenType.TRUE):
        return Literal(True)

    if source.match(TokenType.FALSE):
        return Literal(False)

    if source.match(TokenType.NONE):
        return Literal(None)

    if source.match(TokenType.LEFT_PAREN):
        expr: IExpr = expression(source).unwrap_or_raise()

        if not source.match(TokenType.RIGHT_PAREN):
            raise ParseError(ErrorKinds.EXPECTED_TOKEN, source, TokenType.RIGHT_PAREN)

        return Grouping(expr)

    raise ParseError(ErrorKinds.EXPECTED_TOKEN, source,
                     TokenType.NUMBER,
                     TokenType.STRING,
                     TokenType.TRUE,
                     TokenType.FALSE,
                     TokenType.NONE,
                     TokenType.LEFT_PAREN)


@Catch(ParseError)  # type: ignore
def func_call(source: Source) -> IExpr:
    expr: IExpr = primary(source).unwrap_or_raise()

    while True:
        if source.match(TokenType.LEFT_PAREN):
            args: list[IExpr] = []

            if not source.check(TokenType.RIGHT_PAREN):
                args.append(expression(source).unwrap_or_raise())

                while source.match(TokenType.COMMA):
                    if len(args) >= 255:
                        raise ParseError(ErrorKinds.TOO_MANY_ARGUMENTS, source)
                    args.append(expression(source).unwrap_or_raise())

            if not source.match(TokenType.RIGHT_PAREN):
                raise ParseError(ErrorKinds.EXPECTED_TOKEN, source, TokenType.RIGHT_PAREN)

            expr = FuncCall(expr, args)

        # elif source.match(TokenType.DOT):
        #     name: str = str(source.prev().unwrap_or_raise().value)
        #
        #     if not source.match(TokenType.IDENTIFIER):
        #         raise ParseError(ErrorKinds.EXPECTED_TOKEN, source, TokenType.IDENTIFIER)
        #
        #     expr = Binary(expr, BinaryOp.GET, Identifier(name))

        else:
            break

    return expr


@Catch(ParseError)  # type: ignore
def unary(source: Source) -> IExpr:
    if source.match(TokenType.BANG, TokenType.MINUS):
        operator: UnaryOp = UnaryOp.from_token(source.prev().unwrap_or_raise())
        right: IExpr = unary(source).unwrap_or_raise()
        return Unary(operator, right)

    return func_call(source).unwrap_or_raise()


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
def logical_and(source: Source) -> IExpr:
    expr: IExpr = equality(source).unwrap_or_raise()

    while source.match(TokenType.AND):
        right: IExpr = equality(source).unwrap_or_raise()
        expr = Logical(expr, LogicalOp.AND, right)

    return expr


@Catch(ParseError)  # type: ignore
def logical_or(source: Source) -> IExpr:
    expr: IExpr = logical_and(source).unwrap_or_raise()

    while source.match(TokenType.OR):
        right: IExpr = logical_and(source).unwrap_or_raise()
        expr = Logical(expr, LogicalOp.OR, right)

    return expr


@Catch(ParseError)  # type: ignore
def expression(source: Source) -> IExpr:
    expr: IExpr = logical_or(source).unwrap_or_raise()
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
