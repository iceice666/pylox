from typing import List

from rusty_utils import Result, Option

from src.lexer.error import LexerResult, LexicalErrorKinds, LexicalError
from src.lexer.source import Source
from .tokens import Token, TokenType, KEYWORDS


def __new_token(source: Source, tt: TokenType, value: str) -> Token:
    return Token(
        type=tt,
        value=value,
        lineno=source.line,
        span=(source.start, source.current)
    )


def __try_parse_keyword(keyword: str) -> Option[TokenType]:
    return Option(KEYWORDS.get(keyword))


def __try_parse_string(source: Source) -> LexerResult[Token]:
    while source.peek() != '"':
        if source.peek() is None:
            return Result(err=LexicalError(LexicalErrorKinds.UNTERMINATED_STRING_LITERAL, source=source))

        source.consume()

    lexeme = source.get_lexeme().strip('"')
    token = __new_token(source, TokenType.STRING, lexeme)

    source.consume()  # Closing "

    return Result(ok=token)


def __try_parse_number(source: Source) -> LexerResult[Token]:
    flag_float = False
    while source.has_next():
        ch = source.peek()

        if ch.is_some_and(lambda c: c.is_digit()):
            source.consume()
        elif not flag_float and ch == '.':
            flag_float = True
        elif flag_float and ch == '.':
            return Result(err=LexicalError(LexicalErrorKinds.MALFORMED_NUMBER, source=source))
        else:
            break

    lexeme = source.get_lexeme()
    if len(lexeme) == 0:
        return Result(err=LexicalError(LexicalErrorKinds.HOW_DID_YOU_GET_HERE, source=source))
    else:
        return Result(ok=__new_token(source, TokenType.NUMBER, lexeme))


def __parse_punctuation(
        source: Source,
        default_type: TokenType,
        rules=None) -> LexerResult[Token]:
    if rules is None:
        rules = dict()

    ch = source.peek().unwrap()
    tt: TokenType = rules.get(ch, default_type)
    token = __new_token(source, tt, ch)

    return Result(ok=token)


def scan_token(source: Source) -> LexerResult[Token]:
    ch = source.advance()

    if ch.is_none():
        return Result(ok=Token(type=TokenType.EOF, value='', lineno=source.line, span=(source.start, source.current)))

    ch = ch.unwrap()

    if ch.isspace():
        return Result(err=LexicalError(LexicalErrorKinds.NOP, source=source))

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
        if ch.is_some_and(lambda c: c.isalnum() or c == '_'):
            source.consume()
        else:
            break

    lexeme = source.get_lexeme()
    keyword_type = __try_parse_keyword(lexeme)

    token_type = keyword_type.unwrap_or(TokenType.IDENTIFIER)
    return Result(ok=__new_token(source, token_type, lexeme))


def tokenize(input_: str) -> LexerResult[List[Token]]:
    source = Source(input_)
    tokens: List[Token] = []

    while source.has_next():
        source.reset()
        new_token = scan_token(source)

        match new_token:
            case Result(ok=token):
                tokens.append(token)
            case Result(err=LexicalError(kind=LexicalErrorKinds.NOP)):
                continue
            case Result(err=e):
                return Result(err=e)

    return Result(ok=tokens)
