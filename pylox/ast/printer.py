from typing import List

from rusty_utils import Err, Result, Ok

from pylox.ast.expression import expression, IExpr, Unary, Binary, Grouping, Literal
from pylox.lexer.tokens import Token
from pylox.parser.source import Source


class Resolver:

    def resolve(self, ast: IExpr, indent: int = 0) -> Result[str, ValueError]:
        if isinstance(ast, Unary):
            return self.resolve_unary(ast, indent + 1)
        elif isinstance(ast, Binary):
            return self.resolve_binary(ast, indent + 1)
        elif isinstance(ast, Grouping):
            return self.resolve_grouping(ast, indent + 1)
        elif isinstance(ast, Literal):
            return self.resolve_literal(ast, indent + 1)
        else:
            return Err(ValueError(f"Invalid ast node: {ast}"))

    def resolve_unary(self, value: Unary, indent: int) -> Result[str, ValueError]:
        match self.resolve(value.right, indent):
            case Ok(right):
                return Ok(f"({value.operator} {right})")
            case err:
                return err

    def resolve_binary(self, value: Binary, indent: int) -> Result[str, ValueError]:
        match (self.resolve(value.left, indent), self.resolve(value.right, indent)):
            case (Ok(left), Ok(right)):
                return Ok(f"({value.operator}\n"
                          f"{' ' * indent * 2}{left}\n"
                          f"{' ' * indent * 2}{right}\n"
                          f"{' ' * (indent - 1) * 2})")
            case (err1, err2):
                return err1.and_(err2)

    def resolve_grouping(self, value: Grouping, indent: int) -> Result[str, ValueError]:
        return self.resolve(value.expression, indent).map(
            lambda expr: (f"(\n"
                          f"{' ' * indent * 2}{expr}\n"
                          f"{' ' * (indent - 1) * 2})")
        )

    def resolve_literal(self, value: Literal, _indent: int) -> Result[str, ValueError]:
        return Ok(str(value.value))


def format_ast(input_: List[Token]) -> str | None:
    source = Source(input_)
    ast = expression(source)
    if ast.is_err():
        print(ast.unwrap_err())
        return None

    ast = ast.unwrap()
    resolved = Resolver().resolve(ast, 0)

    return resolved
