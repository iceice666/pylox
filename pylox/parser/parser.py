from typing import List

from pylox.lexer.tokens import Token
from pylox.parser.source import Source


def parse(input_: List[Token]):
    source: Source = Source(input_)