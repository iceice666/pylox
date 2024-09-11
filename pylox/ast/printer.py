from typing import List, Dict

from rusty_utils import Catch

from pylox.ast.expression import expression, IExpr, Unary, Binary, Grouping, Literal, IExprResolver
from pylox.lexer.tokens import Token
from pylox.parser.source import Source


class Resolver(IExprResolver[str, Dict[str, int]]):
    def __init__(self):
        ...

    @Catch(ValueError)
    def resolve(self, ast: IExpr, indent: int = 0) -> str:
        context = {"indent": indent + 1}  # Update the indentation level
        if isinstance(ast, Unary):
            return self.resolve_unary(context, ast).unwrap_or_raise()
        elif isinstance(ast, Binary):
            return self.resolve_binary(context, ast).unwrap_or_raise()
        elif isinstance(ast, Grouping):
            return self.resolve_grouping(context, ast).unwrap_or_raise()
        elif isinstance(ast, Literal):
            return self.resolve_literal(context, ast)
        else:
            raise ValueError(f"Invalid ast node: {ast}")

    @Catch(ValueError)
    def resolve_unary(self, context: Dict[str, int], value: Unary) -> str:
        indent = context.get("indent", 0)
        return f"({self.resolve(value.operator, indent).unwrap_or_raise()} {self.resolve(value.right, indent).unwrap_or_raise()})"

    @Catch(ValueError)
    def resolve_binary(self, context: Dict[str, int], value: Binary) -> str:
        indent = context.get("indent", 0)
        return (f"({value.operator}\n"
                f"{' ' * indent * 2}{self.resolve(value.left, indent).unwrap_or_raise()}\n"
                f"{' ' * indent * 2}{self.resolve(value.right, indent).unwrap_or_raise()}\n"
                f"{' ' * (indent - 1) * 2})")

    @Catch(ValueError)
    def resolve_grouping(self, context: Dict[str, int], value: Grouping) -> str:
        indent = context.get("indent", 0)
        return (f"(\n"
                f"{' ' * indent * 2}{self.resolve(value.expression, indent).unwrap_or_raise()}\n"
                f"{' ' * (indent - 1) * 2})")

    def resolve_literal(self, context: Dict[str, int], value: Literal) -> str:
        return str(value.value)


def print_ast(input_: List[Token]) -> str | None:
    source = Source(input_)
    ast = expression(source)
    if ast.is_err():
        print(ast.unwrap_err())
        return None

    ast = ast.unwrap()
    resolved = Resolver().resolve(ast, 0).unwrap()

    return resolved
