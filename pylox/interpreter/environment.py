import random
import string
from typing import Optional

from rusty_utils import Catch

from pylox.interpreter.error import LoxRuntimeError, ErrorKinds, LoxRuntimeResult


class Environment:
    outer: Optional["Environment"] = None

    stack_name: str = ""
    symbols: dict[str, object] = {}

    def __init__(self,
                 outer: Optional["Environment"] = None,
                 init_symbols: dict[str, object] | None = None,
                 name: str = ""):
        if init_symbols is None:
            init_symbols = {}

        self.outer = outer
        self.symbols = init_symbols
        self.stack_name = name if name else "anonymous"

    def define(self, name: str, value: object) -> None:
        self.symbols[name] = value

    @Catch(LoxRuntimeError)  # type: ignore
    def get(self, name: str) -> object:
        if name in self.symbols:
            return self.symbols[name]
        elif self.outer is not None:
            return self.outer.get(name).unwrap_or_raise()
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

    def __repr__(self) -> str:
        return f"<Environment {self.stack_name} outer={self.outer.__repr__()}>"

    def __str__(self) -> str:
        s = "==============================\n"
        if self.outer is None:
            s += "global environment\n"
        else:
            s += f"stack '{self.stack_name}'\n"
            s = self.outer.__str__() + s

        for name, value in self.symbols.items():
            s += f"{name}: {value}\n"

        return s


class EnvGuard:
    env = Environment(None, {}, "global")

    def get(self, name: str) -> LoxRuntimeResult[object]:
        return self.env.get(name)

    def assign(self, name: str, value: object) -> LoxRuntimeResult[None]:
        return self.env.assign(name, value)

    def define(self, name: str, value: object) -> None:
        return self.env.define(name, value)

    def new_stack(self) -> None:
        name = "anonymous_" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        new_env = Environment(self.env, {}, name)
        self.env = new_env
        pass

    def quit_stack(self) -> None:
        if self.env.outer is None:
            raise LoxRuntimeError(ErrorKinds.INVALID_STATE, None, "Cannot quit global environment.")

        self.env = self.env.outer

    def __str__(self) -> str:
        return str(self.env)

    def __repr__(self) -> str:
        return f"<EnvGuard {self.env}>"
