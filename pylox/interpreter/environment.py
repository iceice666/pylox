from typing import Optional

from rusty_utils import Catch

from pylox.interpreter.error import LoxRuntimeError, ErrorKinds


class Environment:
    outer: Optional["Environment"] = None

    symbols: dict[str, object] = {}

    def __init__(self, outer: Optional["Environment"] = None):
        self.outer = outer

    def define(self, name: str, value: object) -> None:
        self.symbols[name] = value

    @Catch(LoxRuntimeError)  # type: ignore
    def get(self, name: str) -> object:
        if name in self.symbols:
            return self.symbols[name]
        elif self.outer is not None:
            return self.outer.get(name)
        else:
            raise LoxRuntimeError(ErrorKinds.NAME_ERROR, None, f"Undefined variable '{name}'.")

    @Catch(LoxRuntimeError)  # type: ignore
    def assign(self, name: str, value: object) -> None:
        if name in self.symbols:
            self.symbols[name] = value
        elif self.outer is not None:
            self.outer.assign(name, value)
        else:
            raise LoxRuntimeError(ErrorKinds.NAME_ERROR, None, f"Undefined variable '{name}'.")

    def new_stack(self) -> "Environment":
        return Environment(self)

    def __str(self, level: int = 0) -> str:
        ret = ""
        for key, value in self.symbols.items():
            ret += f"{' ' * (level+1)}{key}: {value}\n"
        if self.outer is not None:
            ret += self.outer.__str(level + 1)
        return f"{'  ' * level}{{\n{ret}{'  ' * level}}}"

    def __str__(self) -> str:
        return self.__str(0)
