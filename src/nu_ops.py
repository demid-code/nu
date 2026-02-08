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

    # logic
    NOT = auto()
    AND = auto()
    OR = auto()

    # type casting
    TO_INT = auto()
    TO_FLOAT = auto()

    # read
    READ_8 = auto()
    READ_16 = auto()
    READ_32 = auto()
    READ_64 = auto()

    # write
    WRITE_8 = auto()
    WRITE_16 = auto()
    WRITE_32 = auto()
    WRITE_64 = auto()

    # built-in
    PRINT = auto()
    DROP = auto()
    PICK = auto()
    ROLL = auto()

    # if-else
    IF = auto()
    ELSE = auto()
    ENDIF = auto()

    # while loop
    WHILE = auto()
    DO = auto()
    ENDWHILE = auto()

    # specific
    CMACRO = auto()
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

    # logic
    "not": OpType.NOT,
    "and": OpType.AND,
    "or":  OpType.OR,

    # type casting
    "$int":   OpType.TO_INT,
    "$float": OpType.TO_FLOAT,

    # read
    "@8":  OpType.READ_8,
    "@16": OpType.READ_16,
    "@32": OpType.READ_32,
    "@64": OpType.READ_64,

    # write
    "!8": OpType.WRITE_8,
    "!16": OpType.WRITE_16,
    "!32": OpType.WRITE_32,
    "!64": OpType.WRITE_64,

    # built-in
    "print": OpType.PRINT,
    "drop":  OpType.DROP,
    "pick":  OpType.PICK,
    "roll":  OpType.ROLL,

    # if-else
    "if":    OpType.IF,
    "else":  OpType.ELSE,
    "endif": OpType.ENDIF,

    # while loop
    "while":    OpType.WHILE,
    "do":       OpType.DO,
    "endwhile": OpType.ENDWHILE,
}

@dataclass
class Op:
    type: OpType
    token: Token
    operand: any

    def __repr__(self) -> str:
        return f"{self.type.name}{f": {self.operand}" if self.operand != None else ""}"