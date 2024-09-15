from unittest.mock import MagicMock

import pytest
from rusty_utils import Ok, Result

from pylox.ast.expression import Literal, Grouping, Unary, Binary, BinaryOp, IExpr, UnaryOp
from pylox.lexer.lexer import tokenize
from pylox.lexer.tokens import TokenType
from pylox.parser.error import ParseError
from pylox.parser.expression import expression, synchronize
from pylox.parser.source import Source


def make_expression(source: str) -> Result[IExpr, ParseError]:
    return expression(Source(tokenize(source).unwrap_or_raise()))


def test_primary() -> None:
    source = '42 "hello" True False None'.split()
    expected = [
        Literal(42),
        Literal("hello"),
        Literal(True),
        Literal(False),
        Literal(None),
    ]

    for (src, exp) in zip(source, expected):
        assert make_expression(src) == Ok(exp)


def test_grouping() -> None:
    source = '(42 + 2)'
    expected = Grouping(Binary(Literal(42), BinaryOp.ADD, Literal(2)))

    assert make_expression(source) == Ok(expected)


def test_unary_operations() -> None:
    source = '!true -42'
    expected = [
        Unary(UnaryOp.NOT, Literal(True)),
        Unary(UnaryOp.NEG, Literal(42)),
    ]

    for src, exp in zip(source.split(), expected):
        assert make_expression(src) == Ok(exp)


def test_binary_operations() -> None:
    source = '42 + 2 * 3 - 1'
    expected = Binary(
        Binary(
            Literal(42),
            BinaryOp.ADD,
            Binary(
                Literal(2),
                BinaryOp.MUL,
                Literal(3)
            )
        ),
        BinaryOp.SUB,
        Literal(1)
    )

    assert make_expression(source) == Ok(expected)


def test_comparison_operations() -> None:
    source = '42 > 2 <= 3'
    expected = Binary(
        Binary(
            Literal(42),
            BinaryOp.GT,
            Literal(2)
        ),
        BinaryOp.LE,
        Literal(3)
    )

    assert make_expression(source) == Ok(expected)


def test_equality_operations() -> None:
    source = '42 == 42 != 3'
    expected = Binary(
        Binary(
            Literal(42),
            BinaryOp.EQ,
            Literal(42)
        ),
        BinaryOp.NE,
        Literal(3)
    )

    assert make_expression(source) == Ok(expected)


def test_invalid_expression() -> None:
    with pytest.raises(ParseError):
        make_expression("42 + *").unwrap_or_raise()


def test_nested_grouping() -> None:
    source = '((42 + 2) * 3)'
    expected = Grouping(
        Binary(
            Grouping(
                Binary(Literal(42), BinaryOp.ADD, Literal(2))
            ),
            BinaryOp.MUL,
            Literal(3)
        )
    )

    assert make_expression(source) == Ok(expected)


# FIXME: Synchronization logic is not implemented yet
def test_synchronize() -> None:
    # Testing the synchronization logic after an error
    source = '42 + * ; var x = 10;'

    src_mock = MagicMock(Source)
    src_mock.match.return_value = False
    src_mock.has_next.side_effect = [True, True, True, False]  # Simulate end after some tokens
    src_mock.prev.return_value.type = TokenType.SEMICOLON

    synchronize(src_mock)

    assert src_mock.advance.call_count == 4  # Ensuring advance was called to skip tokens
