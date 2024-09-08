from typing import List

from rusty_utils import Catch

from pylox.lexer.tokens import Token
from pylox.parser.grammar import expression, IExpr, Unary, Binary, Grouping, Literal
from pylox.parser.source import Source


@Catch(ValueError)
def resolve_token(ast: IExpr | Token, indent: int = 0) -> str:
    if isinstance(ast, Token):
        return ast.value

    indent += 1

    if isinstance(ast, Unary):
        return f"({resolve_token(ast.operator, indent).unwrap()} {resolve_token(ast.right, indent).unwrap()})"

    if isinstance(ast, Binary):
        return (f"({resolve_token(ast.operator, indent).unwrap()}\n"
                f"{' ' * indent * 2}{resolve_token(ast.left, indent).unwrap()}\n"
                f"{' ' * indent * 2}{resolve_token(ast.right, indent).unwrap()}\n"
                f"{' ' * (indent - 1) * 2})")

    if isinstance(ast, Grouping):
        return (f"(\n"
                f"{' ' * indent * 2}{resolve_token(ast.expression, indent).unwrap()}\n"
                f"{' ' * (indent - 1) * 2})")

    if isinstance(ast, Literal):
        return str(ast.value)

    raise ValueError(f"Invalid ast node: {ast}")


def print_ast(input_: List[Token]) -> str | None:
    source = Source(input_)
    ast = expression(source)
    if ast.is_err():
        print(ast.unwrap_err())
        return None

    ast = ast.unwrap()
    resolved = resolve_token(ast, 0).unwrap()

    return resolved
