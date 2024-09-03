from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = '('
    RIGHT_PAREN = ')'
    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'
    COMMA = ','
    DOT = '.'
    MINUS = '-'
    PLUS = '+'
    SEMICOLON = ';'
    SLASH = '/'
    STAR = '*'

    # One or two character tokens
    BANG = '!'
    BANG_EQUAL = '!='
    EQUAL = '='
    EQUAL_EQUAL = '=='
    GREATER = '>'
    GREATER_EQUAL = '>='
    LESS = '<'
    LESS_EQUAL = '<='

    # Literals
    IDENTIFIER = 'IDENTIFIER'
    STRING = 'STRING'
    NUMBER = 'NUMBER'

    # Keywords
    AND = 'AND'
    CLASS = 'CLASS'
    ELSE = 'ELSE'
    FALSE = 'FALSE'
    FUN = 'FUN'
    FOR = 'FOR'
    IF = 'IF'
    NIL = 'NIL'
    OR = 'OR'
    PRINT = 'PRINT'
    RETURN = 'RETURN'
    SUPER = 'SUPER'
    THIS = 'THIS'
    TRUE = 'TRUE'
    VAR = 'VAR'
    WHILE = 'WHILE'

    EOF = 'EOF'

    @staticmethod
    def keywords() -> Dict[str, str]:
        return {
            "AND": TokenType.AND,
            "CLASS": TokenType.CLASS,
            "ELSE": TokenType.ELSE,
            "FALSE": TokenType.FALSE,
            "FUN": TokenType.FUN,
            "FOR": TokenType.FOR,
            "IF": TokenType.IF,
            "NIL": TokenType.NIL,
            "OR": TokenType.OR,
            "PRINT": TokenType.PRINT,
            "RETURN": TokenType.RETURN,
            "SUPER": TokenType.SUPER,
            "THIS": TokenType.THIS,
            "TRUE": TokenType.TRUE,
            "VAR": TokenType.VAR,
            "WHILE": TokenType.WHILE,
        }


@dataclass
class Token:
    type: TokenType
    value: str
    lineno: int
    span: (int, int)  # start, end
