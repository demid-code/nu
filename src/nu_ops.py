from enum import IntEnum, auto
from dataclasses import dataclass

from nu_tokens import Token

class OpType(IntEnum):
    # push
    PUSH_INT = auto()
    PUSH_FLOAT = auto()
    PUSH_CSTRING = auto()

    # +, -, *, /
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

    # Type conversions
    TO_INT = auto()
    TO_FLOAT = auto()
    TO_BOOL = auto()

    # Built-in
    PRINT = auto()

    # Specific
    CMACRO = auto()
    EOF = auto()

WORD_TO_OP = {
    # +, -, *, /
    "+": OpType.PLUS,
    "-": OpType.MINUS,
    "*": OpType.MULTIPLY,
    "/": OpType.DIVIDE,

    # Type conversions
    "$int":   OpType.TO_INT,
    "$float": OpType.TO_FLOAT,
    "$bool":  OpType.TO_BOOL,

    # Built-in
    "print": OpType.PRINT,
}

@dataclass
class Op:
    type: OpType
    token: Token
    operand: any

    def __repr__(self) -> str:
        operand = f"{f", {self.operand}" if self.operand != None else ""}"
        return f"{self.type.name}{operand}"