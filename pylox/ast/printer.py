from rusty_utils import Catch

from pylox.ast.expression import *
from pylox.ast.statement import *


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
    elif isinstance(ast, Logical):
        res = resolve_logical(ast, indent + 1).unwrap_or_raise()

    elif isinstance(ast, VarDecl):
        res = resolve_vardecl(ast, indent + 1).unwrap_or_raise()
    elif isinstance(ast, Assignment):
        res = resolve_assignment(ast, indent + 1).unwrap_or_raise()
    elif isinstance(ast, Block):
        res = resolve_block(ast, indent).unwrap_or_raise()
    elif isinstance(ast, IfStmt):
        res = resolve_ifstmt(ast, indent).unwrap_or_raise()
    else:
        raise (ValueError(f"Invalid ast node: {ast}"))

    return res


@Catch(ValueError)  # type: ignore
def resolve_logical(value: Logical, indent: int) -> str:
    left = resolve(value.left, indent).unwrap_or_raise()
    right = resolve(value.right, indent).unwrap_or_raise()
    return (f"({value.operator}\n"
            f"{' ' * indent * 2}{left}\n"
            f"{' ' * indent * 2}{right}\n"
            f"{' ' * (indent - 1) * 2})")


@Catch(ValueError)  # type: ignore
def resolve_ifstmt(value: IfStmt, indent: int) -> str:
    s = (f"{'  ' * indent}(if "
         f"{resolve(value.condition, indent).unwrap_or_raise().strip().replace(' ', '').replace('\n', ' ')}\n")
    s += f"{'  ' * (indent + 1)}{resolve(value.then_branch, indent + 1).unwrap_or_raise()}\n"
    if value.else_branch:
        s += f"{'  ' * (indent + 1)}{resolve(value.else_branch, indent + 1).unwrap_or_raise()}\n"
    s += f"{'  ' * indent})"
    return s


@Catch(ValueError)  # type: ignore
def resolve_block(value: Block, indent: int) -> str:
    s = f"{'  ' * (indent - 1)}(\n"
    for stmt in value.statements:
        s += f"{'  ' * (indent + 1)}{resolve(stmt, indent + 1).unwrap_or_raise()}\n"
    s += f"{'  ' * indent})"
    return s


@Catch(ValueError)  # type: ignore
def resolve_assignment(value: Assignment, indent: int) -> str:
    return f"({value.name} = {resolve(value.value, indent).unwrap_or_raise() if value.value else None})"


@Catch(ValueError)  # type: ignore
def resolve_vardecl(value: VarDecl, indent: int) -> str:
    return f"(var {value.name} = {resolve(value.init, indent).unwrap_or_raise() if value.init else None})"


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
