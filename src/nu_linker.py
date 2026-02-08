from nu_error import Loc, error, exit
from nu_ops import OpType, Op

OPS_TO_LINK = [
    OpType.IF,
    OpType.ELSE,
    OpType.ENDIF,
]

class Linker:
    def __init__(self, ops: list[Op]):
        self.ops = ops
        self.current = 0

        self.stack = []

    def push(self, index: int):
        self.stack.append(index)

    def pop(self) -> tuple[Op, int]:
        index = self.stack.pop()
        return (self.ops[index], index)

    def is_at_end(self) -> bool:
        return self.current >= len(self.ops)
    
    def advance(self) -> tuple[Op, int]:
        index = self.current
        self.current += 1
        return (self.ops[index], index)

    def empty_stack(self, name: str, loc: Loc):
        if len(self.stack) < 0:
            error(f"`{name}` can't be used from top-level", loc); exit(1)

    def solve_stack(self):
        for op_idx in self.stack:
            op = self.ops[op_idx]

            match op.type:
                case OpType.IF:
                    error("`if` was never closed", op.token.loc); exit(1)

                case OpType.ELSE:
                    error("`else` was never closed", op.token.loc); exit(1)

                case _:
                    assert False, f"Unsupported OpType.{op.type.name} in Linker.solve_stack()"

    def scan_op(self):
        op, op_idx = self.advance()

        if op.type in OPS_TO_LINK:
            match op.type:
                case OpType.IF:
                    self.push(op_idx)

                case OpType.ELSE:
                    self.empty_stack("else", op.token.loc)

                    if_op, if_idx = self.pop()
                    if if_op.type != OpType.IF:
                        error("`else` can only close `if`", op.token.loc); exit(1)

                    self.ops[if_idx].operand = op_idx + 1
                    self.push(op_idx)

                case OpType.ENDIF:
                    self.empty_stack("endif", op.token.loc)

                    start_op, start_idx = self.pop()
                    if not start_op.type in (OpType.IF, OpType.ELSE):
                        error("`endif` can only close `if` and `else`"); exit(1)

                    self.ops[start_idx].operand = op_idx + 1

                case _:
                    assert False, f"Unsupported OpType.{op.type.name} in Linker.scan_op()"

    def link(self) -> list[Op]:
        while not self.is_at_end():
            self.scan_op()

        self.solve_stack()

        return self.ops