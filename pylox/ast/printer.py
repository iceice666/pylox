from rusty_utils import Catch, Result, Err

from pylox.ast.expression import *
from pylox.ast.statement import *


def resolve(ast: IExpr | IStmt) -> Result[str, ValueError]:
    res: Result[str, ValueError]

    if isinstance(ast, ExprStmt):
        res = resolve_expr_stmt(ast.expr)
    elif isinstance(ast, PrintStmt):
        res = resolve_print_stmt(ast.expr)
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
    elif isinstance(ast, FuncCall):
        res = resolve_func_call(ast)

    elif isinstance(ast, VarDecl):
        res = resolve_var_decl(ast)
    elif isinstance(ast, Assignment):
        res = resolve_assignment(ast)
    elif isinstance(ast, Block):
        res = resolve_block(ast)
    elif isinstance(ast, IfStmt):
        res = resolve_if_stmt(ast)
    elif isinstance(ast, WhileStmt):
        res = resolve_while_stmt(ast)
    else:
        return Err(ValueError(f"Invalid AST node: {ast}"))

    return res


@Catch(ValueError)  # type: ignore
def resolve_func_call(value: FuncCall) -> str:
    args = ', '.join([resolve(arg).unwrap_or_raise() for arg in value.args])
    return f"(call {value.callee} ({args}))"


@Catch(ValueError)  # type: ignore
def resolve_while_stmt(value: WhileStmt) -> str:
    condition = resolve(value.condition).unwrap_or_raise()
    body = resolve(value.body).unwrap_or_raise()
    return f"(while {condition} {body})"


@Catch(ValueError)  # type: ignore
def resolve_logical(value: Logical) -> str:
    left = resolve(value.left).unwrap_or_raise()
    right = resolve(value.right).unwrap_or_raise()
    return f"({value.operator.value} {left} {right})"


@Catch(ValueError)  # type: ignore
def resolve_if_stmt(value: IfStmt) -> str:
    condition = resolve(value.condition).unwrap_or_raise()
    then_branch = resolve(value.then_branch).unwrap_or_raise()
    else_branch = resolve(value.else_branch).unwrap_or_raise() if value.else_branch else None
    return f"(if {condition} {then_branch} {else_branch})" if else_branch else f"(if {condition} {then_branch})"


@Catch(ValueError)  # type: ignore
def resolve_block(value: Block) -> str:
    statements = ' '.join([resolve(stmt).unwrap_or_raise() for stmt in value.statements])
    return f"(block {statements})"


@Catch(ValueError)  # type: ignore
def resolve_assignment(value: Assignment) -> str:
    expr = resolve(value.value).unwrap_or_raise()
    return f"(= {value.name} {expr})"


@Catch(ValueError)  # type: ignore
def resolve_var_decl(value: VarDecl) -> str:
    init = resolve(value.init).unwrap_or_raise() if value.init else "nil"
    return f"(var {value.name} {init})"


@Catch(ValueError)  # type: ignore
def resolve_expr_stmt(value: IExpr) -> str:
    return f"{resolve(value).unwrap_or_raise()}"


@Catch(ValueError)  # type: ignore
def resolve_print_stmt(value: IExpr) -> str:
    return f"(print {resolve(value).unwrap_or_raise()})"


@Catch(ValueError)  # type: ignore
def resolve_unary(value: Unary) -> str:
    right = resolve(value.right).unwrap_or_raise()
    return f"({value.operator.value} {right})"


@Catch(ValueError)  # type: ignore
def resolve_binary(value: Binary) -> str:
    left = resolve(value.left).unwrap_or_raise()
    right = resolve(value.right).unwrap_or_raise()
    return f"({value.operator.value} {left} {right})"


@Catch(ValueError)  # type: ignore
def resolve_grouping(value: Grouping) -> str:
    expr = resolve(value.expression).unwrap_or_raise()
    return f"(group {expr})"


@Catch(ValueError)  # type: ignore
def resolve_literal(value: Literal) -> str:
    return str(value.value)


@Catch(ValueError)  # type: ignore
def resolve_identifier(value: Identifier) -> str:
    return value.name


@Catch(ValueError)  # type: ignore
def format_ast(ast: Program) -> str:
    return "\n".join([resolve(stmt).unwrap_or_raise() for stmt in ast.statements])
