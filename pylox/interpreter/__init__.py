from pylox.ast.statement import Program
from pylox.interpreter.interpreter import resolve_statement


def interpret(program: Program) -> None:
    for stat in program.statements:
        resolve_statement(stat).unwrap_or_raise()


# REPL
if __name__ == "__main__":
    from pylox.lexer.lexer import tokenize
    from pylox.parser.parser import parse
    from pylox.ast.printer import format_ast

    while True:
        try:
            text = input("|> ")

            match text:
                case ".exit":
                    break
                case ".env":
                    from pylox.interpreter.interpreter import SYMBOLS

                    print(SYMBOLS)
                    continue

            tokens = tokenize(text).unwrap_or_raise()
            ast = parse(tokens).unwrap_or_raise()
            print(format_ast(ast).unwrap_or_raise())
            print("=================================")
            interpret(ast)
        except KeyboardInterrupt:
            break
        except Exception as err:
            print(f"{type(err).__name__}: {err}")
