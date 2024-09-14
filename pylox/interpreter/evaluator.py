from rusty_utils import Err, Ok, Result

from pylox.ast.expression import (
    IExpr,
    Unary,
    UnaryOp,
    Literal,
    Grouping,
    Binary, BinaryOp,
)
from pylox.ast.printer import format_ast
from pylox.interpreter.error import RuntimeErrorKinds
from pylox.parser.expression import expression


def floatify(value: object) -> Result[float, RuntimeError]:
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


class Evaluator:
    symbols: dict[str, object] = {}

    def __init__(self) -> None:
        pass

    def resolve(self, ast: IExpr) -> Result[object, RuntimeError]:
        if isinstance(ast, Literal):
            return self.resolve_literal(ast)

        if isinstance(ast, Grouping):
            return self.resolve_grouping(ast)

        if isinstance(ast, Unary):
            return self.resolve_unary(ast)

        if isinstance(ast, Binary):
            return self.resolve_binary(ast)

        return Err(RuntimeError(RuntimeErrorKinds.UNRECOGNIZED_TOKEN, ast, ""))

    def resolve_literal(self, value: Literal) -> Result[object, RuntimeError]:
        return Ok(value.value)

    def resolve_grouping(self, value: Grouping) -> Result[object, RuntimeError]:
        return self.resolve(value.expression)

    def resolve_unary(self, value: Unary) -> Result[object, RuntimeError]:
        right = self.resolve(value.right)

        match value.operator:
            case UnaryOp.NEG:
                return floatify(right).map(lambda f: -f)

            case UnaryOp.NOT:
                return Ok(not is_truthy(right))

        return Err(RuntimeError(RuntimeErrorKinds.UNREACHABLE, value, "@ resolve_unary"))

    def resolve_binary(self, value: Binary) -> Result[object, RuntimeError]:
        left = self.resolve(value.left).unwrap_or_raise()
        right = self.resolve(value.right).unwrap_or_raise()

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


def interpret(ast: IExpr) -> None:
    print(Evaluator().resolve(ast))


# REPL
if __name__ == "__main__":
    from pylox.lexer.lexer import tokenize
    from pylox.parser.source import Source

    while True:
        try:
            text = input("|> ")
            if text == "exit":
                break
            tokens = tokenize(text).unwrap_or_raise()
            ast = expression(Source(tokens)).unwrap_or_raise()
            print(format_ast(ast).unwrap_or_raise())
            interpret(ast)
        except Exception as err:
            # traceback.print_exc()
            print(f"{type(err).__name__}: {err}")
