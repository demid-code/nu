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

            case OpType.PUSH_BINDED:
                self.writeln(f"Value val = bind_stack.data[bind_stack.size - {op.operand} - 1];", 2)
                self.writeln(f"stack_push(&stack, val);", 2)

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
                self.writeln("stack_push(&stack, value_not(stack_pop(&stack)));", 2)

            case OpType.AND:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_and(a, b));", 2)

            case OpType.OR:
                self.writeln("Value b = stack_pop(&stack);", 2)
                self.writeln("Value a = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, value_or(a, b));", 2)

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

            case OpType.READ_8:
                self.writeln("Value ptr = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, VAL_INT(*(uint8_t*)AS_PTR(ptr)));", 2)

            case OpType.READ_16:
                self.writeln("Value ptr = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, VAL_INT(*(uint16_t*)AS_PTR(ptr)));", 2)

            case OpType.READ_32:
                self.writeln("Value ptr = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, VAL_INT(*(uint32_t*)AS_PTR(ptr)));", 2)

            case OpType.READ_64:
                self.writeln("Value ptr = stack_pop(&stack);", 2)
                self.writeln("stack_push(&stack, VAL_INT(*(uint64_t*)AS_PTR(ptr)));", 2)

            case OpType.WRITE_8:
                self.writeln("Value buf = stack_pop(&stack);", 2)
                self.writeln("Value val = stack_pop(&stack);", 2)
                self.writeln("uint8_t value = AS_INT(value_to_int(val));", 2)
                self.writeln("*(uint8_t*)AS_PTR(buf) = value;", 2)

            case OpType.WRITE_16:
                self.writeln("Value buf = stack_pop(&stack);", 2)
                self.writeln("Value val = stack_pop(&stack);", 2)
                self.writeln("uint16_t value = AS_INT(value_to_int(val));", 2)
                self.writeln("*(uint16_t*)AS_PTR(buf) = value;", 2)

            case OpType.WRITE_32:
                self.writeln("Value buf = stack_pop(&stack);", 2)
                self.writeln("Value val = stack_pop(&stack);", 2)
                self.writeln("uint32_t value = AS_INT(value_to_int(val));", 2)
                self.writeln("*(uint32_t*)AS_PTR(buf) = value;", 2)

            case OpType.WRITE_64:
                self.writeln("Value buf = stack_pop(&stack);", 2)
                self.writeln("Value val = stack_pop(&stack);", 2)
                self.writeln("uint64_t value = AS_INT(value_to_int(val));", 2)
                self.writeln("*(uint64_t*)AS_PTR(buf) = value;", 2)

            case OpType.IF:
                self.writeln("Value condition = stack_pop(&stack);", 2)
                self.writeln("if (!AS_BOOL(value_to_bool(condition)))", 2)
                self.writeln(f"    goto addr_{op.operand};", 2)

            case OpType.ELSE:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.ENDIF:
                pass

            case OpType.WHILE:
                pass

            case OpType.DO:
                self.writeln("Value condition = stack_pop(&stack);", 2)
                self.writeln("if (!AS_BOOL(value_to_bool(condition)))", 2)
                self.writeln(f"    goto addr_{op.operand};", 2)

            case OpType.ENDWHILE:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.BREAK:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.CONTINUE:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.PROC:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.ENDPROC:
                self.writeln("Value ret_addr = stack_pop(&proc_stack);", 2)
                self.writeln("goto *addrs[AS_INT(ret_addr)];", 2)

            case OpType.CALL:
                if op.operand != None:
                    self.writeln(f"stack_push(&proc_stack, VAL_INT({op_idx + 1}));", 2)
                    self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.RETURN:
                self.writeln(f"goto addr_{op.operand};", 2)

            case OpType.IN:
                pass

            case OpType.BIND:
                self.writeln(f"for (int i = 0; i < {op.operand}; i++)", 2)
                self.writeln("    stack_push(&bind_stack, stack_pop(&stack));", 2)

            case OpType.UNBIND | OpType.UNBIND_ALL:
                self.writeln(f"for (int i = 0; i < {op.operand}; i++)", 2)
                self.writeln("    stack_pop(&bind_stack);", 2)

            case OpType.CMACRO:
                self.writeln(f"{op.token.text}", 2)

            case OpType.EOF:
                write_jump = False
                self.writeln("stack_free(&stack);", 2)
                self.writeln("stack_free(&proc_stack);", 2)
                self.writeln("stack_free(&bind_stack);", 2)
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

        self.writeln("ValueStack proc_stack;", 1)
        self.writeln("stack_init(&proc_stack);\n", 1)

        self.writeln("ValueStack bind_stack;", 1)
        self.writeln("stack_init(&bind_stack);\n", 1)

        if len(self.strs) > 0:
            self.writeln("char* strs[] = {%s};" % ", ".join([f"\"{s.encode("unicode_escape").decode()}\"" for s in self.strs]), 1)
        
        self.writeln("void *addrs[] = {%s};" % ", ".join([f"&&addr_{x}" for x in range(len(self.ops))]), 1)

        self.writeln("goto addr_0;\n", 1)

        output = "#include \"nu_runtime.h\"\n\n"
        output += "int main() {\n"
        output += self.writes["init"]
        output += self.writes["main"]
        output += "}\n"

        return output