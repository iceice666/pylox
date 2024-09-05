from rusty_utils import Option


class Source:
    __source: str
    start: int = 0
    current: int = 0
    line: int = 1

    def __init__(self, source: str):
        self.__source = source

    def advance(self) -> Option[str]:
        if not self.has_next():
            return Option()

        ch: str = self.__source[self.current]

        self.current += 1
        if ch == '\n':
            self.line += 1

        return Option(ch)

    def peek(self) -> Option[str]:
        if not self.has_next():
            return Option()
        else:
            return Option(self.__source[self.current])

    def consume(self):
        self.advance()

    def has_next(self) -> bool:
        return self.current < len(self.__source)

    def get_lexeme(self) -> str:
        return self.__source[self.start:self.current]

    def reset(self):
        self.start = self.current
