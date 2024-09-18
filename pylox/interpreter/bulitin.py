from abc import ABC, abstractmethod

from rusty_utils import Ok

from pylox.interpreter.error import LoxRuntimeError, LoxRuntimeResult

class Return(LoxRuntimeError):
    def __init__(self, return_value: object) -> None:
        self. return_value = return_value

    def __repr__ (self) -> str :
        return f"Return({self.return_value})"

    def __str__(self) -> str:
        return self.__repr__()


class LoxCallable(ABC):
    """Base class for Lox callables."""

    @abstractmethod
    def arity(self) -> int:
        """Return the number of arguments the callable takes."""
        pass

    @abstractmethod
    def call(self, args: list[object]) -> LoxRuntimeResult[object]:
        """Call the callable with the given arguments."""
        pass


class TimeImpl(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, args: list[object]) -> LoxRuntimeResult[object]:
        import time
        return Ok(time.time())

    def __repr__(self) -> str:
        return "<native fn time>"


class InputImpl(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, args: list[object]) -> LoxRuntimeResult[object]:
        return Ok(input(args[0]))

    def __repr__(self) -> str:
        return "<native fn input>"

class CastToNumberImpl(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, args: list[object]) -> LoxRuntimeResult[object]:
        # force cast
        return Ok(float(args[0])) # type: ignore

    def __repr__(self) -> str:
        return "<native fn number>"

Builtin = {
    "time": TimeImpl(),
    "input": InputImpl(),
    "number" : CastToNumberImpl(),
}
