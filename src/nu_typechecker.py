from enum import IntEnum, auto

from nu_error import Loc, error, exit
from nu_ops import OpType, Op

class ValueType(IntEnum):
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    BOOL = auto()
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

    def check_arguments(self, amount: int, name: str, loc: Loc):
        if len(self.stack) < amount:
            error(f"not enough arguments for `{name}`", loc); exit(1)

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
                self.check_arguments(2, "+", op.token.loc)

                b_type, _ = self.pop()
                a_type, _ = self.pop()

                if a_type == b_type:
                    if a_type in (ValueType.PTR, ):
                        error(f"can't do {a_type.name} + {b_type.name}", op.token.loc); exit(1)

                    self.push(ValueType.FLOAT if a_type == ValueType.FLOAT else ValueType.INT, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
                
                    if (a_type == ValueType.INT and b_type == ValueType.PTR): self.push(ValueType.PTR, op.token.loc); return
                    if (a_type == ValueType.PTR and b_type == ValueType.INT): self.push(ValueType.PTR, op.token.loc); return

                    error(f"can't do {a_type.name} + {b_type.name}", op.token.loc); exit(1)

            case OpType.MINUS:
                self.check_arguments(2, "-", op.token.loc)

                b_type, _ = self.pop()
                a_type, _ = self.pop()

                if a_type == b_type:
                    self.push(ValueType.FLOAT if a_type == ValueType.FLOAT else ValueType.INT, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
                    
                    if (a_type == ValueType.INT and b_type == ValueType.PTR): self.push(ValueType.PTR, op.token.loc); return
                    if (a_type == ValueType.PTR and b_type == ValueType.INT): self.push(ValueType.PTR, op.token.loc); return

                    error(f"can't do {a_type.name} - {b_type.name}", op.token.loc); exit(1)

            case OpType.MULTIPLY:
                self.check_arguments(2, "*", op.token.loc)

                b_type, _ = self.pop()
                a_type, _ = self.pop()

                if a_type == b_type:
                    if a_type in (ValueType.PTR, ):
                        error(f"can't do {a_type.name} * {b_type.name}", op.token.loc); exit(1)

                    self.push(ValueType.FLOAT if a_type == ValueType.FLOAT else ValueType.INT, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
    
                    error(f"can't do {a_type.name} * {b_type.name}", op.token.loc); exit(1)

            case OpType.DIVIDE:
                self.check_arguments(2, "/", op.token.loc)

                b_type, _ = self.pop()
                a_type, _ = self.pop()

                if a_type == b_type:
                    if a_type in (ValueType.PTR, ):
                        error(f"can't do {a_type.name} / {b_type.name}", op.token.loc); exit(1)

                    self.push(ValueType.FLOAT, op.token.loc)
                else:
                    if (a_type == ValueType.INT and b_type == ValueType.FLOAT): self.push(ValueType.FLOAT, op.token.loc); return
                    if (a_type == ValueType.FLOAT and b_type == ValueType.INT): self.push(ValueType.FLOAT, op.token.loc); return
    
                    error(f"can't do {a_type.name} / {b_type.name}", op.token.loc); exit(1)

            case OpType.TO_INT:
                self.check_arguments(1, "$int", op.token.loc)

                val_type, val_loc = self.pop()
                if val_type == ValueType.PTR:
                    error(f"can't convert {val_type.name.lower()} to int", val_loc); exit(1)

                self.push(ValueType.INT, op.token.loc)

            case OpType.TO_FLOAT:
                self.check_arguments(1, "$float", op.token.loc)

                val_type, val_loc = self.pop()
                if val_type == ValueType.PTR:
                    error(f"can't convert {val_type.name.lower()} to float", val_loc); exit(1)

                self.push(ValueType.FLOAT, op.token.loc)

            case OpType.TO_CHAR:
                self.check_arguments(1, "$char", op.token.loc)

                val_type, val_loc = self.pop()
                if val_type == ValueType.PTR:
                    error(f"can't convert {val_type.name.lower()} to char", val_loc); exit(1)

                self.push(ValueType.CHAR, op.token.loc)

            case OpType.TO_BOOL:
                self.check_arguments(1, "$bool", op.token.loc)

                val_type, val_loc = self.pop()
                if val_type == ValueType.PTR:
                    error(f"can't convert {val_type.name.lower()} to bool", val_loc); exit(1)

                self.push(ValueType.BOOL, op.token.loc)

            case OpType.PRINT:
                self.check_arguments(1, "print", op.token.loc)
                self.pop()

            case OpType.EOF:
                self.check_end_stack()

            case _:
                assert False, f"Unsupported OpType.{op.type.name} in TypeChecker.scan_op()"

    def typecheck(self):
        while not self.is_at_end():
            self.scan_op()