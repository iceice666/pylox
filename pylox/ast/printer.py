from rusty_utils import Catch, Result, Err

from pylox.ast.expression import *
from pylox.ast.statement import *


def resolve(ast: IExpr | IStmt = 0) -> Result[str, ValueError]:
    res: Result[str, ValueError]

    if isinstance(ast, ExprStmt):
        res = resolve_exprstmt(ast.expr)
    elif isinstance(ast, PrintStmt):
        res = resolve_printstmt(ast.expr)
    elif isinstance(ast, Unary):
        res = resolve_unary(ast)
    elif isinstance(ast, Binary):
        res = resolve_binary(ast)
    elif isinstance(ast, Grouping):
        res = resolve_grouping(ast)
    elif isinstance(ast, Literal):
        res = resolve_literal(ast)
    elif isinstance(ast, Identifier):
        res = resolve_identifier(ast)
    elif isinstance(ast, Logical):
        res = resolve_logical(ast)

    elif isinstance(ast, VarDecl):
        res = resolve_vardecl(ast)
    elif isinstance(ast, Assignment):
        res = resolve_assignment(ast)
    elif isinstance(ast, Block):
        res = resolve_block(ast)
    elif isinstance(ast, IfStmt):
        res = resolve_ifstmt(ast)
    elif isinstance(ast, WhileStmt):
        res = resolve_whilestmt(ast)
    else:
        return Err(ValueError(f"Invalid AST node: {ast}"))

    return res


@Catch(ValueError)  # type: ignore
def resolve_whilestmt(value: WhileStmt) -> str:
    condition = resolve(value.condition)
    body = resolve(value.body)
    return f"(while {condition} {body})"


@Catch(ValueError)  # type: ignore
def resolve_logical(value: Logical) -> str:
    left = resolve(value.left)
    right = resolve(value.right)
    return f"({value.operator.value} {left} {right})"


@Catch(ValueError)  # type: ignore
def resolve_ifstmt(value: IfStmt) -> str:
    condition = resolve(value.condition)
    then_branch = resolve(value.then_branch)
    else_branch = resolve(value.else_branch) if value.else_branch else None
    return f"(if {condition} {then_branch} {else_branch})" if else_branch else f"(if {condition} {then_branch})"


@Catch(ValueError)  # type: ignore
def resolve_block(value: Block) -> str:
    statements = ' '.join([resolve(stmt).unwrap_or_raise() for stmt in value.statements])
    return f"(block {statements})"


@Catch(ValueError)  # type: ignore
def resolve_assignment(value: Assignment) -> str:
    expr = resolve(value.value)
    return f"(= {value.name} {expr})"


@Catch(ValueError)  # type: ignore
def resolve_vardecl(value: VarDecl) -> str:
    init = resolve(value.init) if value.init else "nil"
    return f"(var {value.name} {init})"


@Catch(ValueError)  # type: ignore
def resolve_exprstmt(value: IExpr) -> str:
    return f"{resolve(value)}"


@Catch(ValueError)  # type: ignore
def resolve_printstmt(value: IExpr) -> str:
    expr = resolve(value)
    return f"(print {expr})"


@Catch(ValueError)  # type: ignore
def resolve_unary(value: Unary) -> str:
    right = resolve(value.right)
    return f"({value.operator.value} {right})"


@Catch(ValueError)  # type: ignore
def resolve_binary(value: Binary) -> str:
    left = resolve(value.left)
    right = resolve(value.right)
    return f"({value.operator.value} {left} {right})"


@Catch(ValueError)  # type: ignore
def resolve_grouping(value: Grouping) -> str:
    expr = resolve(value.expression)
    return f"(group {expr})"


@Catch(ValueError)  # type: ignore
def resolve_literal(value: Literal, _indent: int) -> str:
    return str(value.value)


@Catch(ValueError)  # type: ignore
def resolve_identifier(value: Identifier, _indent: int) -> str:
    return value.name


@Catch(ValueError)  # type: ignore
def format_ast(ast: Program) -> str:
    return "\n".join([resolve(stmt).unwrap_or_raise() for stmt in ast.statements])
