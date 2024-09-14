from pylox.lexer.error import LexicalErrorKinds
from pylox.lexer.lexer import tokenize
from pylox.lexer.tokens import TokenType, Token


def test_tokenize_happy_path() -> None:
    # 测试正常路径
    input_ = 'var x = 123.45; "hello world";'
    result = tokenize(input_)
    assert result.is_ok()
    tokens = result.unwrap()
    expected_tokens = [
        Token(type=TokenType.VAR, value='var', lineno=1, span=(0, 3)),
        Token(type=TokenType.IDENTIFIER, value='x', lineno=1, span=(4, 5)),
        Token(type=TokenType.EQUAL, value='=', lineno=1, span=(6, 7)),
        Token(type=TokenType.NUMBER, value=123.45, lineno=1, span=(8, 14)),
        Token(type=TokenType.SEMICOLON, value=';', lineno=1, span=(14, 15)),
        Token(type=TokenType.STRING, value='hello world', lineno=1, span=(16, 28)),
        Token(type=TokenType.SEMICOLON, value=';', lineno=1, span=(29, 30)),
    ]
    assert tokens == expected_tokens


def test_tokenize_edge_cases() -> None:
    # 测试边缘情况
    input_ = '123.45.67; "unterminated_string'
    result = tokenize(input_)
    assert result.is_err()
    error = result.unwrap_err()
    assert error.kind == LexicalErrorKinds.MALFORMED_NUMBER

    input_ = '123.45; "unterminated_string'
    result = tokenize(input_)
    assert result.is_err()
    error = result.unwrap_err()
    assert error.kind == LexicalErrorKinds.UNTERMINATED_STRING_LITERAL


def test_try_parse_string() -> None:
    # 测试解析字符串
    result = tokenize('"hello world"')
    assert result.is_ok()
    token = result.unwrap()[0]
    assert token.type == TokenType.STRING
    assert token.value == 'hello world'

    result = tokenize('"unterminated_string')
    assert result.is_err()
    error = result.unwrap_err()
    assert error.kind == LexicalErrorKinds.UNTERMINATED_STRING_LITERAL


def test_try_parse_number() -> None:
    # 测试解析数字
    result = tokenize('123.45')
    assert result.is_ok()
    token = result.unwrap()[0]
    assert token.type == TokenType.NUMBER
    assert token.value == 123.45

    result = tokenize('123.45.67')
    assert result.is_err()
    error = result.unwrap_err()
    assert error.kind == LexicalErrorKinds.MALFORMED_NUMBER


def test_parse_punctuation() -> None:
    # 测试解析标点符号
    result = tokenize('=')
    assert result.is_ok()
    token = result.unwrap()[0]
    assert token.type == TokenType.EQUAL
    assert token.value == '='

    result = tokenize('==')
    assert result.is_ok()
    token = result.unwrap()[0]
    assert token.type == TokenType.EQUAL_EQUAL
    assert token.value == '=='
