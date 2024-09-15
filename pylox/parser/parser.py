from typing import List

from rusty_utils import Catch

from pylox.ast.statement import Program
from pylox.lexer.tokens import Token
from pylox.parser.error import ParseError
from pylox.parser.source import Source
from pylox.parser.statement import program


@Catch(ParseError)  # type: ignore
def parse(input_: List[Token]) -> Program:
    source: Source = Source(input_)
    res: Program = program(source).unwrap_or_raise()
    return res
