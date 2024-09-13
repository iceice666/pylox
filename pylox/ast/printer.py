from typing import List

from rusty_utils import Result, Ok, Catch

from pylox.ast.expression import IExpr, Unary, Binary, Grouping, Literal
from pylox.lexer.tokens import Token
from pylox.parser.error import ParseError
from pylox.parser.expression import expression
from pylox.parser.source import Source


class Printer:

    @Catch(ValueError)  # type: ignore
    def resolve(self, ast: IExpr, indent: int = 0) -> str:
        res: str

        if isinstance(ast, Unary):
            res = self.resolve_unary(ast, indent + 1).unwrap_or_raise()
        elif isinstance(ast, Binary):
            res = self.resolve_binary(ast, indent + 1).unwrap_or_raise()
        elif isinstance(ast, Grouping):
            res = self.resolve_grouping(ast, indent + 1).unwrap_or_raise()
        elif isinstance(ast, Literal):
            res = self.resolve_literal(ast, indent + 1)
        else:
            raise (ValueError(f"Invalid ast node: {ast}"))

        return res

    @Catch(ValueError)  # type: ignore
    def resolve_unary(self, value: Unary, indent: int) -> str:
        right = self.resolve(value.right, indent).unwrap_or_raise()
        return f"({value.operator} {right})"

    @Catch(ValueError)  # type: ignore
    def resolve_binary(self, value: Binary, indent: int) -> str:
        left = self.resolve(value.left, indent).unwrap_or_raise()
        right = self.resolve(value.right, indent).unwrap_or_raise()

        return (f"({value.operator}\n"
                f"{' ' * indent * 2}{left}\n"
                f"{' ' * indent * 2}{right}\n"
                f"{' ' * (indent - 1) * 2})")

    @Catch(ValueError)  # type: ignore
    def resolve_grouping(self, value: Grouping, indent: int) -> str:
        expr = self.resolve(value.expression, indent).unwrap_or_raise()
        return (f"(\n"
                f"{' ' * indent * 2}{expr}\n"
                f"{' ' * (indent - 1) * 2})")

    def resolve_literal(self, value: Literal, _indent: int) -> str:
        return str(value.value)


def format_ast(input_: List[Token]) -> Result[str, ValueError | ParseError]:
    source = Source(input_)
    ast = expression(source)
    match ast:
        case Ok(ast):
            return Printer().resolve(ast, 0)
        case err:
            return err
