from nu_error import Loc, error, exit
from nu_ops import OpType, Op

OPS_TO_LINK = [
    OpType.IF,
    OpType.ELSE,
    OpType.ENDIF,
    OpType.WHILE,
    OpType.DO,
    OpType.ENDWHILE,
    OpType.PROC,
    OpType.ENDPROC,
    OpType.CALL,
]

class Linker:
    def __init__(self, ops: list[Op]):
        self.ops = ops
        self.current = 0

        self.procs = {}

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
                    error("`if` was never closed with `else` or `endif`", op.token.loc); exit(1)

                case OpType.ELSE:
                    error("`else` was never closed with `endif`", op.token.loc); exit(1)

                case OpType.WHILE:
                    error("`while` was never closed with `do`", op.token.loc); exit(1)

                case OpType.DO:
                    error("`do` was never closed with `endwhile`", op.token.loc); exit(1)

                case OpType.PROC:
                    error("`proc` was never closed with `endproc`", op.token.loc); exit(1)

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

                case OpType.WHILE:
                    self.push(op_idx)

                case OpType.DO:
                    self.empty_stack("do", op.token.loc)

                    while_op, while_idx = self.pop()
                    if while_op.type != OpType.WHILE:
                        error("`do` can only close `while`", op.token.loc); exit(1)

                    self.ops[op_idx].operand = while_idx
                    self.push(op_idx)

                case OpType.ENDWHILE:
                    self.empty_stack("endwhile", op.token.loc)

                    do_op, do_idx = self.pop()
                    if do_op.type != OpType.DO:
                        error("`endwhile` can only close `do`", op.token.loc); exit(1)

                    self.ops[op_idx].operand = do_op.operand + 1
                    self.ops[do_idx].operand = op_idx + 1

                case OpType.PROC:
                    self.procs[op.operand] = {"start": op_idx}
                    self.push(op_idx)

                case OpType.ENDPROC:
                    self.empty_stack("endproc", op.token.loc)

                    proc, proc_idx = self.pop()
                    if proc.type != OpType.PROC:
                        error("`endproc` can only close `proc`", op.token.loc); exit(1)

                    self.ops[proc_idx].operand = op_idx + 1

                case OpType.CALL:
                    if op.token.text in self.procs:
                        self.ops[op_idx].operand = self.procs[op.token.text]["start"] + 1
                    else:
                        assert False, f"Call to unexisten procedure in Linker.scan_op()"

                case _:
                    assert False, f"Unsupported OpType.{op.type.name} in Linker.scan_op()"

    def link(self) -> list[Op]:
        while not self.is_at_end():
            self.scan_op()

        self.solve_stack()

        return self.ops