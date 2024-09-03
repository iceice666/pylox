import unittest
from typing import List, Optional

from result import Ok, Err, is_ok, is_err

from src.lexer.error import LexerResult, LexicalErrorKinds, LexicalError
from src.lexer.source import Source
from src.lexer.tokens import Token, TokenType


def __new_token(source: Source, tt: TokenType, value: str) -> Token:
    return Token(
        type=tt,
        value=value,
        lineno=source.line,
        span=(source.start, source.current)
    )


def __try_parse_keyword(keyword: str) -> Optional[TokenType]:
    return TokenType.keywords().get(keyword)


def __try_parse_string(source: Source) -> LexerResult[Token]:
    while source.peek() != '"':
        if source.peek() is None:
            return Err(LexicalError(LexicalErrorKinds.UNTERMINATED_STRING_LITERAL, source=source))

        source.consume()

    lexeme = source.get_lexeme().strip('"')
    token = __new_token(source, TokenType.STRING, lexeme)

    source.consume()  # Closing "

    return Ok(token)


def __try_parse_number(source: Source) -> LexerResult[Token]:
    flag_float = False
    while source.has_next():
        ch = source.peek()

        if ch is not None and ch.isdigit():
            source.consume()
        elif not flag_float and ch == '.':
            flag_float = True
        elif flag_float and ch == '.':
            return Err(LexicalError(LexicalErrorKinds.MALFORMED_NUMBER, source=source))
        else:
            break

    lexeme = source.get_lexeme()
    if len(lexeme) == 0:
        return Err(LexicalError(LexicalErrorKinds.HOW_DID_YOU_GET_HERE, source=source))
    else:
        return Ok(__new_token(source, TokenType.NUMBER, lexeme))


def __parse_punctuation(source: Source, default_type: TokenType, rules: Optional[dict[str, TokenType]] = None) -> (
        LexerResult)[Token]:
    ch = source.peek()
    tt: TokenType = rules.get(ch, default_type)
    token = __new_token(source, tt, ch)

    return Ok(token)


def scan_token(source: Source) -> LexerResult[Token]:
    ch = source.advance()

    if ch is None:
        return Ok(Token(type=TokenType.EOF, value='', lineno=source.line, span=(source.start, source.current)))

    if ch.isspace():
        return Err(LexicalError(LexicalErrorKinds.NOP, source=source))

    if ch.isdigit():
        return __try_parse_number(source)

    if ch == '"':
        return __try_parse_string(source)

    match ch:
        case '(':
            return __parse_punctuation(source, TokenType.LEFT_PAREN)
        case ')':
            return __parse_punctuation(source, TokenType.RIGHT_PAREN)
        case '{':
            return __parse_punctuation(source, TokenType.LEFT_BRACE)
        case '}':
            return __parse_punctuation(source, TokenType.RIGHT_BRACE)
        case ',':
            return __parse_punctuation(source, TokenType.COMMA)
        case '.':
            return __parse_punctuation(source, TokenType.DOT)
        case ';':
            return __parse_punctuation(source, TokenType.SEMICOLON)
        case '+':
            return __parse_punctuation(source, TokenType.PLUS)
        case '-':
            return __parse_punctuation(source, TokenType.MINUS)
        case '*':
            return __parse_punctuation(source, TokenType.STAR)
        case '/':
            return __parse_punctuation(source, TokenType.SLASH)

        case '!':
            return __parse_punctuation(source, TokenType.BANG, {'=': TokenType.BANG_EQUAL})
        case '=':
            return __parse_punctuation(source, TokenType.EQUAL, {'=': TokenType.EQUAL_EQUAL})
        case '<':
            return __parse_punctuation(source, TokenType.LESS, {'=': TokenType.LESS_EQUAL})
        case '>':
            return __parse_punctuation(source, TokenType.GREATER, {'=': TokenType.GREATER_EQUAL})

    # fallback
    while source.has_next():
        ch = source.peek()
        if ch.isalnum() or ch == '_':
            source.consume()
        else:
            break

    lexeme = source.get_lexeme()
    keyword_type = __try_parse_keyword(lexeme)

    token_type = keyword_type if keyword_type else TokenType.IDENTIFIER
    return Ok(__new_token(source, token_type, lexeme))


def tokenize(input_: str) -> LexerResult[List[Token]]:
    source = Source(input_)
    tokens: List[Token] = []

    while source.has_next():
        source.reset()
        new_token = scan_token(source)

        match new_token:
            case Ok(token):
                tokens.append(token)
            case Err(LexicalError(kind=LexicalErrorKinds.NOP)):
                continue
            case Err(e):
                return Err(e)

    return Ok(tokens)


class TestLexer(unittest.TestCase):
    def test_scan_token_happy_path(self):
        source = Source('123')
        result = scan_token(source)
        self.assertTrue(is_ok(result))
        self.assertEqual(result.ok_value.type, TokenType.NUMBER)
        self.assertEqual(result.ok_value.value, '123')

    def test_scan_token_edge_cases(self):
        source = Source('')
        result = scan_token(source)
        self.assertTrue(is_ok(result))
        self.assertEqual(result.ok_value.type, TokenType.EOF)

        source = Source('   ')
        result = scan_token(source)
        self.assertTrue(is_err(result))
        self.assertEqual(result.err_value.kind, LexicalErrorKinds.NOP)

        source = Source('"unterminated string')
        result = scan_token(source)
        self.assertTrue(is_err(result))
        self.assertEqual(result.err_value.kind, LexicalErrorKinds.UNTERMINATED_STRING_LITERAL)

        source = Source('123..456')
        result = scan_token(source)
        self.assertTrue(is_err(result))
        self.assertEqual(result.err_value.kind, LexicalErrorKinds.MALFORMED_NUMBER)

    def test_tokenize_happy_path(self):
        result = tokenize('123 "string"')
        self.assertTrue(is_ok(result))
        tokens = result.ok_value
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].type, TokenType.STRING)

    def test_tokenize_edge_cases(self):
        result = tokenize('')
        self.assertTrue(is_ok(result))
        self.assertEqual(len(result.ok_value), 0)

        result = tokenize('   ')
        self.assertTrue(is_ok(result))
        self.assertEqual(len(result.ok_value), 0)

        result = tokenize('123 "unterminated string')
        self.assertTrue(is_err(result))
        self.assertEqual(result.err_value.kind, LexicalErrorKinds.UNTERMINATED_STRING_LITERAL)

        result = tokenize('123..456 "string"')
        self.assertTrue(is_err(result))
        self.assertEqual(result.err_value.kind, LexicalErrorKinds.MALFORMED_NUMBER)


if __name__ == '__main__':
    unittest.main()
