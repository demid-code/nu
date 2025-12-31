from nu_error import Loc, report_error
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

    def push(self, op_idx: int):
        self.stack.append(op_idx)

    def pop(self) -> tuple[Op, int]:
        idx = self.stack.pop()
        return (self.ops[idx], idx)

    def is_at_end(self) -> bool:
        return self.current >= len(self.ops)
    
    def advance(self) -> tuple[Op, int]:
        idx = self.current
        self.current += 1
        return (self.ops[idx], idx)

    def empty_stack_error(self, name: str, loc: Loc):
        if len(self.stack) <= 0: report_error(f"`{name}` can't be used from top-level", loc)

    def solve_stack(self):
        for op_idx in self.stack:
            op = self.ops[op_idx]

            match op.type:
                case _:
                    assert False, f"Unsupported OpType.{op.type.name} in Linker.solve_stack()"

    def scan_op(self):
        op, op_idx = self.advance()

        if op.type in OPS_TO_LINK:
            match op.type:
                case OpType.IF:
                    self.push(op_idx)
                
                case OpType.ELSE:
                    self.empty_stack_error("else", op.token.loc)

                    if_op, if_idx = self.pop()
                    if if_op.type != OpType.IF:
                        report_error("`else` can only close `if`", op.token.loc)

                    self.ops[if_idx].operand = op_idx + 1
                    self.push(op_idx)

                case OpType.ENDIF:
                    self.empty_stack_error("endif", op.token.loc)

                    opp, opp_idx = self.pop()
                    if not opp.type in (OpType.IF, OpType.ELSE):
                        report_error("`endif` can only close `if` and `else`", op.token.loc)

                    self.ops[opp_idx].operand = op_idx + 1

                case _:
                    assert False, f"Unsupported OpType.{op.type.name} in Linker.scan_op()"

    def link(self) -> list[Op]:
        while not self.is_at_end():
            self.scan_op()
        
        return self.ops