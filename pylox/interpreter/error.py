from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypeVar, TypeAlias

from rusty_utils import Result

from pylox.ast.expression import IExpr
from pylox.ast.statement import IStmt


class RuntimeErrorKinds(Enum):
    NAME_ERROR = "Name Error"
    UNREACHABLE = "Unreachable"
    VALUE_ERROR = "Value Error"
    UNRECOGNIZED_TOKEN = "Unrecognized Token"


@dataclass
class RuntimeError(Exception):
    kind: RuntimeErrorKinds
    token: IExpr | IStmt | None = None
    message: Optional[str] = None

    def __str__(self) -> str:
        string = f"{self.kind.value}"
        if self.token:
            string += f" with token {self.token}"
        if self.message:
            string += f": {self.message}"
        return string


_T = TypeVar('_T', covariant=True)
RuntimeResult: TypeAlias = Result[_T, RuntimeError]
