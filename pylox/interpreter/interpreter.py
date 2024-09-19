from rusty_utils import Err, Ok, Catch, Option

from pylox.ast.expression import (
    IExpr, Unary, UnaryOp, Literal, Grouping, Binary, BinaryOp, Identifier, LogicalOp, FuncCall,
)
from pylox.ast.printer import format_ast
from pylox.ast.statement import IStmt, ExprStmt, VarDecl, Assignment, Block, IfStmt, WhileStmt, Program
from pylox.interpreter.bulitin import LoxCallable
from pylox.interpreter.environment import EnvGuard
from pylox.interpreter.error import ErrorKinds, LoxRuntimeResult, LoxRuntimeError
from pylox.lexer.lexer import tokenize
from pylox.parser.parser import parse

SYMBOLS = EnvGuard()


############### Helper Functions ##############

def floatify(value: object) -> LoxRuntimeResult[float]:
    """Convert a value to float if possible, otherwise return an error."""
    if not isinstance(value, (int, float, str)):
        return Err(LoxRuntimeError(
            ErrorKinds.VALUE_ERROR,
            None,
            f"Operand must be a number. Got: {value}",
        ))

    return Ok(float(value))


def is_truthy(value: object) -> bool:
    """Determine the truthiness of a value."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return bool(value)


def is_equal(left: object, right: object) -> bool:
    """Check if two values are equal."""
    if left is None and right is None:
        return True
    if left is None:
        return False
    return left == right


@Catch(LoxRuntimeError)  # type: ignore
def not_matched(obj: IStmt | IExpr) -> None:
    """Raise an error for unrecognized tokens."""
    raise LoxRuntimeError(ErrorKinds.UNRECOGNIZED_TOKEN, obj, "")


############### Expression Resolver ##############

def resolve_expression(expr: IExpr) -> LoxRuntimeResult[object]:
    """Resolve an expression based on its type."""
    table = {
        "Literal": resolve_literal,
        "Grouping": resolve_grouping,
        "Identifier": resolve_identifier,
        "Unary": resolve_unary,
        "Binary": resolve_binary,
        "Logical": resolve_logical,
        "FuncCall": resolve_func_call,
    }

    clazz = type(expr).__name__
    resolver = Option(table.get(clazz)).unwrap_or(not_matched)
    return resolver(expr)


def resolve_literal(value: Literal) -> LoxRuntimeResult[object]:
    """Resolve a literal expression."""
    return Ok(value.value)


def resolve_grouping(value: Grouping) -> LoxRuntimeResult[object]:
    """Resolve a grouping expression."""
    return resolve_expression(value.expression)


def resolve_identifier(value: Identifier) -> LoxRuntimeResult[object]:
    """Resolve an identifier expression."""
    return SYMBOLS.get(value.name)


def resolve_unary(value: Unary) -> LoxRuntimeResult[object]:
    """Resolve a unary expression."""
    right = resolve_expression(value.right)

    match value.operator:
        case UnaryOp.NEG:
            return floatify(right).map(lambda f: -f)
        case UnaryOp.NOT:
            return Ok(not is_truthy(right))

    return Err(LoxRuntimeError(ErrorKinds.UNREACHABLE, value, "@ resolve_unary"))


def resolve_binary(value: Binary) -> LoxRuntimeResult[object]:
    """Resolve a binary expression."""
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


def resolve_logical(value: Binary) -> LoxRuntimeResult[object]:
    """Resolve a logical expression."""
    left = resolve_expression(value.left).unwrap_or_raise()
    logic_left = is_truthy(left)

    match value.operator:
        case LogicalOp.AND:
            if not logic_left:
                return Ok(left)
        case LogicalOp.OR:
            if logic_left:
                return Ok(left)

    return resolve_expression(value.right)


def resolve_func_call(value: FuncCall) -> LoxRuntimeResult[object]:
    """Resolve a function call expression."""
    callee = resolve_expression(value.callee).unwrap_or_raise()
    args = [resolve_expression(arg).unwrap_or_raise() for arg in value.args]

    if not isinstance(callee, LoxCallable):
        return Err(LoxRuntimeError(
            ErrorKinds.TYPE_ERROR,
            value,
            f"Can only call functions and classes. Got: {callee}",
        ))

    if len(args) != callee.arity():
        return Err(LoxRuntimeError(
            ErrorKinds.RUNTIME_ERROR,
            value,
            f"Expected {callee.arity()} arguments but got {len(args)}",
        ))

    return callee.call(args)


############### Statement Resolver ##############

def resolve_statement(stat: IStmt) -> LoxRuntimeResult[None]:
    """Resolve a statement based on its type."""
    table = {
        "ExprStmt": resolve_expr_stmt,
        "VarDecl": resolve_var_decl,
        "Assignment": resolve_assignment,
        "Block": resolve_block,
        "IfStmt": resolve_if_stmt,
        "WhileStmt": resolve_while_stmt,
    }

    clazz = type(stat).__name__
    resolver = Option(table.get(clazz)).unwrap_or(not_matched)
    return resolver(stat)


@Catch(LoxRuntimeError)  # type: ignore
def resolve_while_stmt(stat: WhileStmt) -> None:
    """Resolve a while statement."""
    while is_truthy(resolve_expression(stat.condition).unwrap_or_raise()):
        resolve_statement(stat.body).unwrap_or_raise()


@Catch(LoxRuntimeError)  # type: ignore
def resolve_if_stmt(stat: IfStmt) -> None:
    """Resolve an if statement."""
    condition = is_truthy(resolve_expression(stat.condition).unwrap_or_raise())
    if condition:
        resolve_statement(stat.then_branch).unwrap_or_raise()
    elif stat.else_branch:
        resolve_statement(stat.else_branch).unwrap_or_raise()


@Catch(LoxRuntimeError)  # type: ignore
def resolve_expr_stmt(stat: ExprStmt) -> None:
    """Resolve an expression statement."""
    resolve_expression(stat.expr).unwrap_or_raise()


@Catch(LoxRuntimeError)  # type: ignore
def resolve_var_decl(stat: VarDecl) -> None:
    """Resolve a variable declaration."""
    value = resolve_expression(stat.init).unwrap_or_raise() if stat.init else None
    SYMBOLS.define(stat.name, value)


@Catch(LoxRuntimeError)  # type: ignore
def resolve_assignment(stat: Assignment) -> None:
    """Resolve an assignment statement."""
    value = resolve_expression(stat.value).unwrap_or_raise()
    SYMBOLS.assign(stat.name, value)


@Catch(LoxRuntimeError)  # type: ignore
def resolve_block(stat: Block) -> None:
    """Resolve a block statement."""
    SYMBOLS.new_stack()
    for stmt in stat.statements:
        resolve_statement(stmt).unwrap_or_raise()
    SYMBOLS.quit_stack()


############### Interpreter ##############


def interpret(program: Program) -> None:
    for stat in program.statements:
        resolve_statement(stat).unwrap_or_raise()


# REPL
if __name__ == "__main__":
    while True:
        try:
            text = input("|> ")

            match text:
                case ".exit":
                    break
                case ".newscope":
                    SYMBOLS.new_stack()
                    continue
                case ".quitscope":
                    SYMBOLS.quit_stack()
                    continue
                case ".env":
                    print(SYMBOLS)
                    continue
                case ".read":
                    with open("./input.lox", "r", encoding="utf-8") as f:
                        text = f.read()

            tokens = tokenize(text).unwrap_or_raise()
            print(f"Tokens:")
            for i, token in enumerate(tokens):
                print(f"{i + 1}) {token}")
            print()
            ast = parse(tokens).unwrap_or_raise()
            print("AST:")
            print(format_ast(ast).unwrap_or_raise())
            print("=================================")

            interpret(ast)
        except KeyboardInterrupt:
            break
        except Exception as err:
            print(f"{type(err).__name__}: {err}")
