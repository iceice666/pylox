from rusty_utils import Err, Ok, Catch, Option

from pylox.ast.expression import (
    IExpr,
    Unary, UnaryOp,
    Literal, Grouping,
    Binary, BinaryOp, Identifier,
)
from pylox.ast.statement import IStmt, PrintStmt, ExprStmt, VarDecl, Assignment
from pylox.interpreter.environment import Environment
from pylox.interpreter.error import ErrorKinds, RuntimeResult, LoxRuntimeError

SYMBOLS: Environment = Environment()


############### Helper Functions ##############

def floatify(value: object) -> RuntimeResult[float]:
    if not isinstance(value, (int, float)):
        return Err(LoxRuntimeError(
            ErrorKinds.VALUE_ERROR,
            None,
            f"Operand must be a number. Got: {value}",
        ))

    if isinstance(value, float):
        return Ok(value)
    if isinstance(value, int):
        return Ok(float(value))
    if isinstance(value, str):
        return Ok(float(value))

    return Ok(float(str(value)))


def is_truthy(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value)
    return True


def is_equal(left: object, right: object) -> bool:
    if left is None and right is None:
        return True

    if left is None:
        return False

    return left == right


@Catch(LoxRuntimeError)  # type: ignore
def not_matched(obj: IStmt | IExpr) -> None:
    raise LoxRuntimeError(ErrorKinds.UNRECOGNIZED_TOKEN, obj, "")


############### Expression Resolver ##############
def resolve_expression(expr: IExpr) -> RuntimeResult[object]:
    table = {
        "Literal": resolve_literal,
        "Grouping": resolve_grouping,
        "Identifier": resolve_identifier,
        "Unary": resolve_unary,
        "Binary": resolve_binary,
    }

    clazz = type(expr).__name__
    resolver = Option(table.get(clazz)).unwrap_or(not_matched)
    return resolver(expr)


def resolve_literal(value: Literal) -> RuntimeResult[object]:
    return Ok(value.value)


def resolve_grouping(value: Grouping) -> RuntimeResult[object]:
    return resolve_expression(value.expression)


def resolve_identifier(value: Identifier) -> RuntimeResult[object]:
    return SYMBOLS.get(value.name)


def resolve_unary(value: Unary) -> RuntimeResult[object]:
    right = resolve_expression(value.right)

    match value.operator:
        case UnaryOp.NEG:
            return floatify(right).map(lambda f: -f)

        case UnaryOp.NOT:
            return Ok(not is_truthy(right))

    return Err(LoxRuntimeError(ErrorKinds.UNREACHABLE, value, "@ resolve_unary"))


def resolve_binary(value: Binary) -> RuntimeResult[object]:
    left = resolve_expression(value.left).unwrap_or_raise()
    right = resolve_expression(value.right).unwrap_or_raise()

    match value.operator:
        case BinaryOp.EQ:
            return Ok(is_equal(left, right))
        case BinaryOp.NE:
            return Ok(not is_equal(left, right))

    left = floatify(left).unwrap_or_raise()
    right = floatify(right).unwrap_or_raise()

    match value.operator:
        case BinaryOp.ADD:
            return Ok(left + right)
        case BinaryOp.SUB:
            return Ok(left - right)
        case BinaryOp.MUL:
            return Ok(left * right)
        case BinaryOp.DIV:
            return Ok(left / right)
        case BinaryOp.LE:
            return Ok(left <= right)
        case BinaryOp.LS:
            return Ok(left < right)
        case BinaryOp.GE:
            return Ok(left >= right)
        case BinaryOp.GT:
            return Ok(left > right)

    return Err(LoxRuntimeError(ErrorKinds.UNREACHABLE, value, "@ resolve_binary"))


############### Statement Resolver ##############
def resolve_statement(stat: IStmt) -> RuntimeResult[None]:
    table = {
        "PrintStmt": resolve_print_stmt,
        "ExprStmt": resolve_expr_stmt,
        "VarDecl": resolve_var_decl,
        "Assignment": resolve_assignment,
    }

    clazz = type(stat).__name__
    resolver = Option(table.get(clazz)).unwrap_or(not_matched)
    return resolver(stat)


@Catch(LoxRuntimeError)  # type: ignore
def resolve_print_stmt(stat: PrintStmt) -> None:
    expr = resolve_expression(stat.expr).unwrap_or_raise()
    print(expr)


@Catch(LoxRuntimeError)  # type: ignore
def resolve_expr_stmt(stat: ExprStmt) -> None:
    resolve_expression(stat.expr).unwrap_or_raise()


@Catch(LoxRuntimeError)  # type: ignore
def resolve_var_decl(stat: VarDecl) -> None:
    value = resolve_expression(stat.init).unwrap_or_raise() if stat.init else None
    SYMBOLS.define(stat.name, value)


@Catch(LoxRuntimeError)  # type: ignore
def resolve_assignment(stat: Assignment) -> None:
    value = resolve_expression(stat.value).unwrap_or_raise()
    SYMBOLS.assign(stat.name, value)
