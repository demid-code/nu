from enum import IntEnum, auto
from dataclasses import dataclass

from nu_tokens import Token

# TODO: push str
class OpType(IntEnum):
    # push
    PUSH_INT = auto()
    PUSH_FLOAT = auto()
    PUSH_STRING = auto()

    # arithmetic
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

    # comparing
    EQUAL = auto()
    GREATER = auto()
    LESS = auto()

    # type casting
    TO_INT = auto()
    TO_FLOAT = auto()

    # built-in
    PRINT = auto()
    DROP = auto()

    # specific
    EOF = auto()

WORD_TO_OPTYPE = {
    # arithmetic
    "+": OpType.PLUS,
    "-": OpType.MINUS,
    "*": OpType.MULTIPLY,
    "/": OpType.DIVIDE,

    # comparing
    "==": OpType.EQUAL,
    ">":  OpType.GREATER,
    "<":  OpType.LESS,

    # type casting
    "$int":   OpType.TO_INT,
    "$float": OpType.TO_FLOAT,

    # built-in
    "print": OpType.PRINT,
    "drop":  OpType.DROP,
}

@dataclass
class Op:
    type: OpType
    token: Token
    operand: any

    def __repr__(self) -> str:
        return f"{self.token.loc}: {self.type.name}{f": {self.operand}" if self.operand != None else ""}"