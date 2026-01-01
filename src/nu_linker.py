from nu_error import Loc, report_error
from nu_ops import OpType, Op

OPS_TO_LINK = [
    OpType.IF,
    OpType.ELSE,
    OpType.ENDIF,
    OpType.WHILE,
    OpType.DO,
    OpType.ENDWHILE,
    OpType.BREAK,
    OpType.CONTINUE,
    OpType.PROC,
    OpType.ENDPROC,
    OpType.CALL,
    OpType.RETURN,
]

class Linker:
    def __init__(self, ops: list[Op]):
        self.ops = ops
        self.current = 0

        self.procs = {}

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
                case OpType.IF:
                    report_error("`if` was never closed with `endif`", op.token.loc)

                case OpType.ELSE:
                    report_error("`else` was never closed with `endif`", op.token.loc)

                case OpType.WHILE:
                    report_error("`while` was never closed with `do`", op.token.loc)

                case OpType.DO:
                    report_error("`do` was never closed with `endwhile`", op.token.loc)

                case OpType.PROC:
                    report_error("`proc` was never closed with `endproc`", op.token.loc)

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

                case OpType.WHILE:
                    self.push(op_idx)

                case OpType.DO:
                    self.empty_stack_error("do", op.token.loc)

                    while_op, while_idx = self.pop()
                    if while_op.type != OpType.WHILE:
                        report_error("`do` can only close `while`", op.token.loc)

                    self.ops[op_idx].operand = while_idx
                    self.push(op_idx)

                case OpType.ENDWHILE:
                    self.empty_stack_error("endwhile", op.token.loc)

                    do_op, do_idx = self.pop()
                    if do_op.type != OpType.DO:
                        report_error("`endwhile` can only close `do`", op.token.loc)

                    self.ops[op_idx].operand = do_op.operand + 1
                    self.ops[do_idx].operand = op_idx + 1

                case OpType.BREAK:
                    self.empty_stack_error("break", op.token.loc)

                    found = False
                    for idx, opp in enumerate(self.ops[op_idx+1:]):
                        opp_idx = idx + op_idx + 1
                        
                        if opp.type == OpType.ENDWHILE:
                            self.ops[op_idx].operand = opp_idx + 1

                            found = True
                            break

                    if not found:
                        report_error("`break` can only be used inside while loop")

                case OpType.CONTINUE:
                    self.empty_stack_error("continue", op.token.loc)

                    found = False
                    for idx, opp in enumerate(self.ops[op_idx+1:]):
                        opp_idx = idx + op_idx + 1
                        
                        if opp.type == OpType.ENDWHILE:
                            self.ops[op_idx].operand = opp_idx

                            found = True
                            break

                    if not found:
                        report_error("`continue` can only be used inside while loop")

                case OpType.PROC:
                    self.push(op_idx)

                case OpType.ENDPROC:
                    self.empty_stack_error("endproc", op.token.loc)

                    proc, proc_idx = self.pop()
                    if proc.type != OpType.PROC:
                        report_error("`endproc` can only close `proc`", proc.token.loc)

                    proc_name = self.ops[proc_idx + 1].token.text

                    self.ops[proc_idx].operand = op_idx + 1
                    self.procs[proc_name] = {"start": proc_idx}

                case OpType.CALL:
                    if op.token.text in self.procs:
                        self.ops[op_idx].operand = self.procs[op.token.text]["start"] + 3

                case OpType.RETURN:
                    self.empty_stack_error("return", op.token.loc)

                    found = False
                    for idx, opp in enumerate(self.ops[op_idx+1:]):
                        opp_idx = idx + op_idx + 1
                        
                        if opp.type == OpType.ENDPROC:
                            self.ops[op_idx].operand = opp_idx

                            found = True
                            break

                    if not found:
                        report_error("`return` can only be used inside procedure")

                case _:
                    assert False, f"Unsupported OpType.{op.type.name} in Linker.scan_op()"

    def link(self) -> list[Op]:
        while not self.is_at_end():
            self.scan_op()

        self.solve_stack()
        
        return self.ops