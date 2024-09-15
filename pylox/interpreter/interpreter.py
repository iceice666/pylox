from rusty_utils import Err, Ok

from pylox.ast.expression import (
    IExpr,
    Unary, UnaryOp,
    Literal, Grouping,
    Binary, BinaryOp, Identifier,
)
from pylox.ast.statement import IStmt, PrintStmt, ExprStmt
from pylox.interpreter.error import RuntimeErrorKinds, RuntimeResult, RuntimeError

SYMBOLS: dict[str, object] = {}


############### Helper Functions ##############

def floatify(value: object) -> RuntimeResult[float]:
    if not isinstance(value, (int, float)):
        return Err(RuntimeError(
            RuntimeErrorKinds.VALUE_ERROR,
            None,
            "Operand must be a number.",
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


############### Expression Resolver ##############
def resolve_expression(expr: IExpr) -> RuntimeResult[object]:
    if isinstance(expr, Literal):
        return resolve_literal(expr)

    if isinstance(expr, Grouping):
        return resolve_grouping(expr)

    if isinstance(expr, Identifier):
        return resolve_identifier(expr)

    if isinstance(expr, Unary):
        return resolve_unary(expr)

    if isinstance(expr, Binary):
        return resolve_binary(expr)

    return Err(RuntimeError(RuntimeErrorKinds.UNRECOGNIZED_TOKEN, expr, ""))


def resolve_literal(value: Literal) -> RuntimeResult[object]:
    return Ok(value.value)


def resolve_grouping(value: Grouping) -> RuntimeResult[object]:
    return resolve_expression(value.expression)


def resolve_identifier(value: Identifier) -> RuntimeResult[object]:
    if value.name in SYMBOLS:
        return Ok(SYMBOLS[value.name])

    return Err(RuntimeError(RuntimeErrorKinds.NAME_ERROR, value, f"Undefined variable '{value.name}'."))


def resolve_unary(value: Unary) -> RuntimeResult[object]:
    right = resolve_expression(value.right)

    match value.operator:
        case UnaryOp.NEG:
            return floatify(right).map(lambda f: -f)

        case UnaryOp.NOT:
            return Ok(not is_truthy(right))

    return Err(RuntimeError(RuntimeErrorKinds.UNREACHABLE, value, "@ resolve_unary"))


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

    return Err(RuntimeError(RuntimeErrorKinds.UNREACHABLE, value, "@ resolve_binary"))


############### Statement Resolver ##############
def resolve_statement(stat: IStmt) -> RuntimeResult[None]:
    if isinstance(stat, PrintStmt):
        return resolve_print_stmt(stat)

    if isinstance(stat, ExprStmt):
        return resolve_expr_stmt(stat)


def resolve_print_stmt(stat: PrintStmt) -> RuntimeResult[None]:
    expr = resolve_expression(stat.expr).unwrap_or_raise()
    print(expr)
    return Ok(None)


def resolve_expr_stmt(stat: ExprStmt) -> RuntimeResult[None]:
    resolve_expression(stat.expr).unwrap_or_raise()
    return Ok(None)
