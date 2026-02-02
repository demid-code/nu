from enum import IntEnum, auto
from dataclasses import dataclass

from nu_tokens import Token

# TODO: push str
class OpType(IntEnum):
    # push
    PUSH_INT = auto()
    PUSH_FLOAT = auto()

    # arithmetic
    PLUS = auto()

    # built-in
    PRINT = auto()

    # specific
    EOF = auto()

WORD_TO_OPTYPE = {
    # arithmetic
    "+": OpType.PLUS,

    # built-in
    "print": OpType.PRINT,
}

@dataclass
class Op:
    type: OpType
    token: Token
    operand: any

    def __repr__(self) -> str:
        return f"{self.token.loc}: {self.type.name}{f": {self.operand}" if self.operand != None else ""}"