from rusty_utils import Catch

from pylox.ast.expression import IExpr, Unary, Binary, Grouping, Literal, Identifier
from pylox.ast.statement import IStmt, ExprStmt, PrintStmt, Program, VarDecl


@Catch(ValueError)  # type: ignore
def resolve(ast: IExpr | IStmt, indent: int = 0) -> str:
    res: str

    if isinstance(ast, ExprStmt):
        res = resolve_exprstmt(ast.expr, indent).unwrap_or_raise()
    elif isinstance(ast, PrintStmt):
        res = resolve_printstmt(ast.expr, indent).unwrap_or_raise()
    elif isinstance(ast, Unary):
        res = resolve_unary(ast, indent + 1).unwrap_or_raise()
    elif isinstance(ast, Binary):
        res = resolve_binary(ast, indent + 1).unwrap_or_raise()
    elif isinstance(ast, Grouping):
        res = resolve_grouping(ast, indent + 1).unwrap_or_raise()
    elif isinstance(ast, Literal):
        res = resolve_literal(ast, indent + 1)
    elif isinstance(ast, Identifier):
        res = resolve_identifier(ast, indent + 1)
    elif isinstance(ast, VarDecl):
        res = resolve_vardecl(ast, indent + 1).unwrap_or_raise()
    else:
        raise (ValueError(f"Invalid ast node: {ast}"))

    return res


@Catch(ValueError)  # type: ignore
def resolve_vardecl(value: VarDecl, indent: int) -> str:
    return f"(var {value.name} {resolve(value.init, indent).unwrap_or_raise() if value.init else None})"


@Catch(ValueError)  # type: ignore
def resolve_exprstmt(value: IExpr, indent: int) -> str:
    return f"({resolve(value, indent).unwrap_or_raise()})"


@Catch(ValueError)  # type: ignore
def resolve_printstmt(value: IExpr, indent: int) -> str:
    return f"(print {resolve(value, indent).unwrap_or_raise()})"


@Catch(ValueError)  # type: ignore
def resolve_unary(value: Unary, indent: int) -> str:
    right = resolve(value.right, indent).unwrap_or_raise()
    return f"({value.operator} {right})"


@Catch(ValueError)  # type: ignore
def resolve_binary(value: Binary, indent: int) -> str:
    left = resolve(value.left, indent).unwrap_or_raise()
    right = resolve(value.right, indent).unwrap_or_raise()

    return (f"({value.operator}\n"
            f"{' ' * indent * 2}{left}\n"
            f"{' ' * indent * 2}{right}\n"
            f"{' ' * (indent - 1) * 2})")


@Catch(ValueError)  # type: ignore
def resolve_grouping(value: Grouping, indent: int) -> str:
    expr = resolve(value.expression, indent).unwrap_or_raise()
    return (f"(\n"
            f"{' ' * indent * 2}{expr}\n"
            f"{' ' * (indent - 1) * 2})")


def resolve_literal(value: Literal, _indent: int) -> str:
    return str(value.value)


def resolve_identifier(value: Identifier, _indent: int) -> str:
    return value.name


@Catch(ValueError)  # type: ignore
def format_ast(ast: Program) -> str:
    return "\n".join([resolve(stmt, 0).unwrap_or_raise() for stmt in ast.statements])
