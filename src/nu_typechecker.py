from enum import IntEnum, auto

from nu_error import Loc, error, exit
from nu_ops import OpType, Op

class ValueType(IntEnum):
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    PTR = auto()

class TypeChecker:
    def __init__(self, ops: list[Op]):
        self.ops = ops
        self.current = 0

        self.stack = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.ops)
    
    def advance(self) -> Op:
        self.current += 1
        return self.ops[self.current - 1]
    
    def push(self, type: ValueType, loc: Loc):
        self.stack.append((type, loc))

    def pop(self) -> tuple[ValueType, Loc]:
        return self.stack.pop()

    def check_end_stack(self):
        if len(self.stack) != 0:
            val = self.stack[-1]
            error(f"{val[0].name.lower()} left on the stack", val[1])
            exit(1)

    def scan_op(self):
        op = self.advance()

        match op.type:
            case OpType.PUSH_INT:   self.push(ValueType.INT, op.token.loc)
            case OpType.PUSH_FLOAT: self.push(ValueType.FLOAT, op.token.loc)
            case OpType.PUSH_CHAR:  self.push(ValueType.CHAR, op.token.loc)

            case OpType.PLUS:
                if len(self.stack) < 2:
                    error("not enough arguments for `+`", op.token.loc); exit(1)

                b_type, b_loc = self.pop()
                a_type, a_loc = self.pop()

                if a_type == b_type:
                    if a_type in (ValueType.PTR, ):
                        error(f"can't do {a_type.name} + {b_type.name}", op.token.loc); exit(1)

                    self.push(a_type, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
                
                    if (a_type == ValueType.INT and b_type == ValueType.PTR): self.push(ValueType.PTR, op.token.loc); return
                    if (a_type == ValueType.PTR and b_type == ValueType.INT): self.push(ValueType.PTR, op.token.loc); return

                    error(f"can't do {a_type.name} + {b_type.name}", op.token.loc); exit(1)

            case OpType.MINUS:
                if len(self.stack) < 2:
                    error("not enough arguments for `-`", op.token.loc); exit(1)

                b_type, b_loc = self.pop()
                a_type, a_loc = self.pop()

                if a_type == b_type:
                    self.push(a_type, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
                    
                    if (a_type == ValueType.INT and b_type == ValueType.PTR): self.push(ValueType.PTR, op.token.loc); return
                    if (a_type == ValueType.PTR and b_type == ValueType.INT): self.push(ValueType.PTR, op.token.loc); return

                    error(f"can't do {a_type.name} - {b_type.name}", op.token.loc); exit(1)

            case OpType.MULTIPLY:
                if len(self.stack) < 2:
                    error("not enough arguments for `*`", op.token.loc); exit(1)

                b_type, b_loc = self.pop()
                a_type, a_loc = self.pop()

                if a_type == b_type:
                    if a_type in (ValueType.PTR, ):
                        error(f"can't do {a_type.name} * {b_type.name}", op.token.loc); exit(1)

                    self.push(a_type, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
    
                    error(f"can't do {a_type.name} * {b_type.name}", op.token.loc); exit(1)

            case OpType.DIVIDE:
                if len(self.stack) < 2:
                    error("not enough arguments for `/`", op.token.loc); exit(1)

                b_type, b_loc = self.pop()
                a_type, a_loc = self.pop()

                if a_type == b_type:
                    if a_type in (ValueType.PTR, ):
                        error(f"can't do {a_type.name} / {b_type.name}", op.token.loc); exit(1)

                    self.push(ValueType.FLOAT, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
    
                    error(f"can't do {a_type.name} / {b_type.name}", op.token.loc); exit(1)

            case OpType.PRINT:
                if len(self.stack) < 1:
                    error("not enough arguments for `print`", op.token.loc); exit(1)
                
                self.pop()

            case OpType.EOF:
                self.check_end_stack()

            case _:
                assert False, f"Unsupported OpType.{op.type.name} in TypeChecker.scan_op()"

    def typecheck(self):
        while not self.is_at_end():
            self.scan_op()