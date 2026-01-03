from enum import IntEnum, auto
from dataclasses import dataclass

from nu_tokens import Token

class OpType(IntEnum):
    # push
    PUSH_INT = auto()
    PUSH_FLOAT = auto()
    PUSH_CSTRING = auto()
    PUSH_BINDED = auto()

    # +, -, *, /
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

    # Comparison
    EQUAL = auto()
    GREATER = auto()
    LESS = auto()

    # Logical
    NOT = auto()
    AND = auto()
    OR = auto()

    # Type conversions
    TO_INT = auto()
    TO_FLOAT = auto()
    TO_BOOL = auto()

    # Built-in
    PRINT = auto()
    DROP = auto()
    PICK = auto()
    ROLL = auto()

    # Read
    READ_8 = auto()
    READ_16 = auto()
    READ_32 = auto()
    READ_64 = auto()

    # Write
    WRITE_8 = auto()
    WRITE_16 = auto()
    WRITE_32 = auto()
    WRITE_64 = auto()

    # If/Else
    IF = auto()
    ELSE = auto()
    ENDIF = auto()

    # While loop
    WHILE = auto()
    DO = auto()
    ENDWHILE = auto()
    BREAK = auto()
    CONTINUE = auto()

    # Procedure
    PROC = auto()
    ENDPROC = auto()
    CALL = auto()
    RETURN = auto()

    # Binding
    BIND = auto()
    UNBIND = auto()
    UNBIND_ALL = auto()

    # Block forming
    IN = auto()

    # Specific
    CMACRO = auto()
    EOF = auto()

WORD_TO_OP = {
    # +, -, *, /
    "+": OpType.PLUS,
    "-": OpType.MINUS,
    "*": OpType.MULTIPLY,
    "/": OpType.DIVIDE,

    # Comparison
    "==": OpType.EQUAL,
    ">":  OpType.GREATER,
    "<":  OpType.LESS,

    # Logical
    "not": OpType.NOT,
    "and": OpType.AND,
    "or":  OpType.OR,

    # Type conversions
    "$int":   OpType.TO_INT,
    "$float": OpType.TO_FLOAT,
    "$bool":  OpType.TO_BOOL,

    # Built-in
    "print": OpType.PRINT,
    "drop":  OpType.DROP,
    "pick":  OpType.PICK,
    "roll":  OpType.ROLL,

    # Read
    "@8":  OpType.READ_8,
    "@16": OpType.READ_16,
    "@32": OpType.READ_32,
    "@64": OpType.READ_64,

    # Write
    "!8":  OpType.WRITE_8,
    "!16": OpType.WRITE_16,
    "!32": OpType.WRITE_32,
    "!64": OpType.WRITE_64,

    # If/Else
    "if":    OpType.IF,
    "else":  OpType.ELSE,
    "endif": OpType.ENDIF,

    # While loop
    "while":    OpType.WHILE,
    "do":       OpType.DO,
    "endwhile": OpType.ENDWHILE,
    "break":    OpType.BREAK,
    "continue": OpType.CONTINUE,

    # Procedure
    "proc":    OpType.PROC,
    "endproc": OpType.ENDPROC,
    "return":  OpType.RETURN,

    # Binding
    "unbind": OpType.UNBIND,

    # Block forming
    "in": OpType.IN,
}

@dataclass
class Op:
    type: OpType
    token: Token
    operand: any

    def __repr__(self) -> str:
        operand = f"{f", {self.operand}" if self.operand != None else ""}"
        return f"{self.type.name}{operand}"