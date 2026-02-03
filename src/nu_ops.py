from enum import IntEnum, auto
from dataclasses import dataclass

from nu_tokens import Token

# TODO: push str
class OpType(IntEnum):
    # push
    PUSH_INT = auto()
    PUSH_FLOAT = auto()
    PUSH_CHAR = auto()

    # arithmetic
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

    # type casting
    TO_INT = auto()
    TO_FLOAT = auto()
    TO_CHAR = auto()
    TO_BOOL = auto()

    # built-in
    PRINT = auto()

    # specific
    EOF = auto()

WORD_TO_OPTYPE = {
    # arithmetic
    "+": OpType.PLUS,
    "-": OpType.MINUS,
    "*": OpType.MULTIPLY,
    "/": OpType.DIVIDE,

    # type casting
    "$int":   OpType.TO_INT,
    "$float": OpType.TO_FLOAT,
    "$char":  OpType.TO_CHAR,
    "$bool":  OpType.TO_BOOL,

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