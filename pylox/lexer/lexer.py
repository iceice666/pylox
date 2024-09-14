from typing import List, Dict

from rusty_utils import Option, Err, Ok

from pylox.lexer.error import LexerResult, LexicalErrorKinds, LexicalError
from pylox.lexer.source import Source
from .tokens import Token, TokenType, KEYWORDS


def __new_token(source: Source, tt: TokenType, value: object) -> Token:
    return Token(
        type=tt,
        value=value,
        lineno=source.line,
        span=(source.start, source.current)
    )


def __try_parse_keyword(keyword: str) -> Option[TokenType]:
    return Option(KEYWORDS.get(keyword))


def __try_parse_string(source: Source) -> LexerResult[Token]:
    while True:
        next_ch = source.peek()
        if next_ch .is_none():
            return Err(LexicalError(LexicalErrorKinds.UNTERMINATED_STRING_LITERAL, source=source))

        if next_ch .is_some_and(lambda c : c == '"'):
            break

        source.consume()



    lexeme = source.get_lexeme().strip('"')
    token = __new_token(source, TokenType.STRING, lexeme)

    source.consume()  # Closing "

    return Ok(token)


def __try_parse_number(source: Source) -> LexerResult[Token]:
    flag_float = False
    while source.has_next():
        ch = source.peek()

        if ch.is_some_and(lambda c: c.isdigit()):
            source.consume()
        elif ch.is_some_and(lambda c: c == '.'):
            if flag_float:
                return Err(LexicalError(LexicalErrorKinds.MALFORMED_NUMBER, source=source))
            flag_float = True
            source.consume()
        else:
            break

    lexeme = source.get_lexeme()
    if len(lexeme) == 0:
        return Err(LexicalError(LexicalErrorKinds.HOW_DID_YOU_GET_HERE, source=source))
    else:
        return Ok(__new_token(source, TokenType.NUMBER, float(lexeme) if flag_float else int(lexeme)))


def __parse_punctuation(
        source: Source,
        default_type: TokenType,
        rules: Dict[str, TokenType] | None = None) -> LexerResult[Token]:
    if rules is None:
        rules = dict()

    base = source.get_lexeme()
    next_ch = source.peek()

    if next_ch.is_some_and(lambda c: c in rules):
        next_ch = source.advance().unwrap()
        return Ok(__new_token(source, rules[next_ch], base + next_ch))
    else:
        return Ok(__new_token(source, default_type, base))


def scan_token(source: Source) -> LexerResult[Token]:
    ch = source.advance()

    ch = ch.unwrap()

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
        if ch.is_some_and(lambda c: c.isalnum() or c == '_'):
            source.consume()
        else:
            break

    lexeme = source.get_lexeme()
    keyword_type = __try_parse_keyword(lexeme)

    token_type = keyword_type.unwrap_or(TokenType.IDENTIFIER)
    return Ok(__new_token(source, token_type, lexeme))


def tokenize(input_: str) -> LexerResult[List[Token]]:
    source: Source = Source(input_)
    tokens: List[Token] = []

    while source.has_next():
        source.reset()
        new_token = scan_token(source)

        match new_token:
            case Ok(tok):
                tokens.append(tok)
            case Err(LexicalError(kind=LexicalErrorKinds.NOP)):
                continue
            case Err(err):
                return Err(err)


    return Ok(tokens)
