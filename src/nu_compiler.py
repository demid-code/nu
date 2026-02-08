from nu_ops import OpType, Op

class Compiler:
    def __init__(self, ops: list[Op]):
        self.ops = ops
        self.current = 0

        self.write_mode = None
        self.writes = {"init": "", "main": ""}

        self.strs = []

    def write(self, txt: str, tabs: int = 0):
        self.writes[self.write_mode] += f"{"    " * tabs}{txt}"

    def writeln(self, txt: str, tabs: int = 0):
        self.writes[self.write_mode] += f"{"    " * tabs}{txt}\n"

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

            case OpType.PUSH_STRING:
                if not op.operand in self.strs:
                    self.strs.append(op.operand)

                idx = self.strs.index(op.operand)
                self.writeln(f"stack_push(&stack, VAL_PTR(strs[{idx}]));", 2)

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

            case OpType.EQUAL:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_equal(a, b));", 2)

            case OpType.GREATER:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_greater(a, b));", 2)

            case OpType.LESS:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_less(a, b));", 2)

            case OpType.NOT:
                self.writeln("stack_push(&stack, VAL_INT(!value_as_bool(stack_pop(&stack))));", 2)

            case OpType.AND:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, VAL_INT(value_as_bool(a) && value_as_bool(b)));")

            case OpType.OR:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, VAL_INT(value_as_bool(a) || value_as_bool(b)));")

            case OpType.PRINT:
                self.writeln("value_print(stack_pop(&stack));", 2)

            case OpType.DROP:
                self.writeln("stack_pop(&stack);", 2)

            case OpType.PICK:
                self.writeln("Value index = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, stack_pick(&stack, AS_INT(index)));", 2)

            case OpType.ROLL:
                self.writeln("Value index = stack_pop(&stack);", 2)
                self.writeln("stack_roll(&stack, AS_INT(index));", 2)

            case OpType.IF:
                self.writeln("Value condition = stack_pop(&stack);", 2)
                self.writeln(f"if (!value_as_bool(condition)) goto addr_{op.operand};", 2)

            case OpType.ELSE:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.ENDIF:
                pass

            case OpType.CMACRO:
                self.writeln(op.operand, 2)

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
            self.writeln("char* strs[] = {%s};\n" % ", ".join(f"\"{x}\"" for x in self.strs), 1)

        self.writeln("goto addr_0;\n", 1)

        output = "#include \"nu_runtime.h\"\n\n"
        output += "int main() {\n"
        output += self.writes["init"]
        output += self.writes["main"]
        output += "}\n"

        return output