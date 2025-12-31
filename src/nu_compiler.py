from nu_ops import OpType, Op

class Compiler:
    def __init__(self, ops: list[Op]):
        self.ops = ops
        self.current = 0

        self.strs = []

        self.writes = {"init": "", "main": ""}
        self.write_mode = None

    def write(self, code: str, tabs: int = 0):
        self.writes[self.write_mode] += f"{"    " * tabs}{code}"

    def writeln(self, code: str, tabs: int = 0):
        self.writes[self.write_mode] += f"{"    " * tabs}{code}\n"

    def is_at_end(self) -> bool:
        return self.current >= len(self.ops)
    
    def advance(self) -> tuple[Op, int]:
        idx = self.current
        self.current += 1
        return (self.ops[idx], idx)
    
    def scan_op(self):
        op, op_idx = self.advance()

        write_jump = True
        self.writeln(f"addr_{op_idx}: %s // {op.type.name}" % "{", 1)

        match op.type:
            case OpType.PUSH_INT:
                self.writeln(f"stack_push(&stack, VAL_INT({op.operand}));", 2)

            case OpType.PUSH_FLOAT:
                self.writeln(f"stack_push(&stack, VAL_FLOAT({op.operand}));", 2)

            case OpType.PUSH_CSTRING:
                if not op.operand in self.strs:
                    self.strs.append(op.operand)

                self.writeln(f"stack_push(&stack, VAL_PTR(strs[{self.strs.index(op.operand)}]));", 2)

            case OpType.PLUS:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_add(a, b));", 2)

            case OpType.MINUS:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_sub(a, b));", 2)

            case OpType.MULTIPLY:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_mul(a, b));", 2)

            case OpType.DIVIDE:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_div(a, b));", 2)

            case OpType.TO_INT:
                self.writeln("stack_push(&stack, value_to_int(stack_pop(&stack)));", 2)

            case OpType.TO_FLOAT:
                self.writeln("stack_push(&stack, value_to_float(stack_pop(&stack)));", 2)

            case OpType.TO_BOOL:
                self.writeln("stack_push(&stack, value_to_bool(stack_pop(&stack)));", 2)

            case OpType.PRINT:
                self.writeln("value_print(stack_pop(&stack));", 2)

            case OpType.DROP:
                self.writeln("stack_pop(&stack);", 2)

            case OpType.PICK:
                self.writeln("Value index = stack_pop(&stack);", 2)
                self.writeln("stack_pick(&stack, (size_t)AS_INT(index));", 2)

            case OpType.ROLL:
                self.writeln("Value index = stack_pop(&stack);", 2)
                self.writeln("stack_roll(&stack, (size_t)AS_INT(index));", 2)

            case OpType.CMACRO:
                self.writeln(f"{op.token.text}", 2)

            case OpType.EOF:
                write_jump = False
                self.writeln("stack_free(&stack);", 2)
                self.writeln("return 0;", 2)

            case _:
                assert False, f"Unsupported OpType.{op.type.name} in Compiler.scan_op()"

        if write_jump:
            self.writeln(f"goto addr_{op_idx + 1};", 2)
        self.writeln("}", 1)

    def compile(self) -> str:
        self.write_mode = "main"
        while not self.is_at_end():
            self.scan_op()

        self.write_mode = "init"
        
        self.writeln("ValueStack stack;", 1)
        self.writeln("stack_init(&stack);\n", 1)

        if len(self.strs) > 0:
            self.writeln("char* strs[] = {%s};" % ", ".join([f"\"{s.encode("unicode_escape").decode()}\"" for s in self.strs]), 1)
        
        self.writeln("goto addr_0;\n", 1)

        output = "#include \"nu_runtime.h\"\n\n"
        output += "int main() {\n"
        output += self.writes["init"]
        output += self.writes["main"]
        output += "}\n"

        return output