from typing import AnyStr, Optional


class Source:
    __source: str
    start: int = 0
    current: int = 0
    line: int = 1

    def __init__(self, source: AnyStr):
        self.__source = source

    def advance(self) -> Optional[str]:
        if not self.has_next():
            return None

        ch: str = self.__source[self.current]

        self.current += 1
        if ch == '\n':
            self.line += 1

        return ch

    def peek(self) -> Optional[str]:
        if not self.has_next():
            return None
        else:
            return self.__source[self.current]

    def consume(self):
        self.advance()

    def has_next(self) -> bool:
        return self.current < len(self.__source)

    def get_lexeme(self) -> str:
        return self.__source[self.start:self.current]

    def reset(self):
        self.start = self.current
