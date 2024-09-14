from pylox.ast.printer import format_ast
from pylox.lexer.lexer import tokenize


def test_printer() -> None:
    expected = """
(+
  11
  (/
    (*
      45
      2
    )
    (
      (-
        3
        1
      )
    )
  )
)
""".strip()

    tokens = tokenize("11 + 45 * 2 / (3 - 1)").unwrap()
    result = format_ast(tokens).unwrap_or_raise()

    assert result == expected
