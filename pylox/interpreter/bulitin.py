from abc import ABC, abstractmethod

from rusty_utils import Ok

from pylox.interpreter.error import LoxRuntimeResult


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


class __Time_Impl(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, args: list[object]) -> LoxRuntimeResult[object]:
        import time
        return Ok(time.time())

    def __repr__(self) -> str:
        return "<native fn time>"


Builtin = {
    "time": __Time_Impl()
}
