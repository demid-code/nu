from nu_error import Loc, error, note, exit
from nu_tokens import TokenType, Token
from nu_ops import OpType, WORD_TO_OPTYPE, Op
from nu_evaluator import Evaluator

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

        self.ops = []

        self.mems = {}
        self.procs = {}

        self.proc_stack = []

        self.bind_names = []
        self.bind_stack = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def advance(self) -> tuple[Token, int]:
        index = self.current
        self.current += 1
        return (self.tokens[index], index)

    def add_op(self, op_type: OpType, token: Token, operand: any = None):
        self.ops.append(Op(op_type, token, operand))

    def make_op(self):
        token, token_idx = self.advance()

        match token.type:
            case TokenType.INT:
                self.add_op(OpType.PUSH_INT, token, token.text)

            case TokenType.FLOAT:
                self.add_op(OpType.PUSH_FLOAT, token, token.text)

            case TokenType.CHAR:
                char = token.text.encode().decode("unicode_escape")
                self.add_op(OpType.PUSH_INT, token, str(ord(char)))

            case TokenType.STRING:
                self.add_op(OpType.PUSH_STRING, token, token.text)

            case TokenType.WORD:
                if token.text == "mem":
                    if self.is_at_end():
                        error("expected `mem` name", token.loc); exit(1)

                    name, name_idx = self.advance()
                    if name.type != TokenType.WORD:
                        error("expected `mem` name to be a valid word", name.loc); exit(1)

                    found_end = False

                    while True:
                        tok, tok_idx = self.advance()
                        if tok.type == TokenType.WORD:
                            if tok.text == "mem":
                                error("can't define `mem` inside `mem`", tok.loc); exit(1)

                            if tok.text == "endmem":
                                found_end = True
                                break

                    if not found_end:
                        error("`mem` was never closed", token.loc); exit(1)

                    proc_mem = len(self.proc_stack) > 0
                    proc_mem_idx = -1

                    mem_size = Evaluator(self.tokens[name_idx+1:self.current-1]).evaluate()[0]

                    if proc_mem:
                        proc_name = self.proc_stack[-1]

                        if not "mems" in self.procs[proc_name]:
                            self.procs[proc_name]["mems"] = {}

                        proc_mem_idx = len(self.procs[proc_name]["mems"].keys())
                        self.procs[proc_name]["mems"][name.text] = {"mem_idx": proc_mem_idx, "size": mem_size}
                    else:
                        self.mems[name.text] = {"size": mem_size}
                elif token.text in self.mems:
                    mem = self.mems[token.text]
                    self.add_op(OpType.PUSH_MEM, token)
                elif token.text == "proc":
                    if self.is_at_end():
                        error("expected procedure name", token.loc); exit(1)

                    name, name_idx = self.advance()
                    if name.type != TokenType.WORD:
                        error("expected procedure name to be a valid word", name.loc);exit(1)

                    if name.text in self.procs:
                        error("can't redefine an already existing procedure", token.loc)
                        note("original procedure located here", self.tokens[self.procs[name.text]["start"]].loc)
                        exit(1)

                    self.add_op(OpType.PROC, token, name.text)
                    self.procs[name.text] = {"op_start": len(self.ops) - 1}

                    self.proc_stack.append(name.text)

                    return
                elif token.text == "endproc":
                    proc_name = self.proc_stack.pop()
                    
                    if "mems" in self.procs[proc_name]:
                        self.ops.insert(self.procs[proc_name]["op_start"] + 1, Op(OpType.PREP_PROC_MEM, None, proc_name))
                        self.add_op(OpType.FREE_PROC_MEM, token, len(self.procs[proc_name]["mems"].keys()))

                    self.add_op(OpType.ENDPROC, token)
                    return
                elif token.text in self.procs:
                    self.add_op(OpType.CALL, token)
                elif token.text == "let":
                    if self.is_at_end():
                        error("expected let name bindings", token.loc); exit(1)

                    found_in = False

                    names = []
                    while not self.is_at_end():
                        tok, tok_idx = self.advance()
                        if tok.type != TokenType.WORD:
                            error("expected let name binding to be a valid word", tok.loc); exit(1)

                        if tok.text == "in":
                            found_in = True
                            break

                        names.append(tok.text)

                    if not found_in:
                        error("`let` was never closed with `in`", token.loc); exit(1)

                    self.bind_names.extend(list(reversed(names)))
                    self.bind_stack.append(len(names))

                    self.add_op(OpType.BIND, token, len(names))
                elif token.text in self.bind_names:
                    self.add_op(OpType.PUSH_BINDED, token, len(self.bind_names) - self.bind_names.index(token.text) - 1)
                elif token.text == "endlet":
                    bind_len = self.bind_stack.pop()
                    for _ in range(bind_len): self.bind_names.pop()
                    self.add_op(OpType.UNBIND, token, bind_len)
                elif token.text in WORD_TO_OPTYPE:
                    self.add_op(WORD_TO_OPTYPE.get(token.text), token)
                else:
                    if len(self.proc_stack) > 0:
                        for proc_name in reversed(self.proc_stack):
                            proc = self.procs[proc_name]

                            if ("mems" in proc) and (token.text in proc["mems"]):
                                self.add_op(OpType.PUSH_PROC_MEM, token, len(proc["mems"].keys()) - proc["mems"][token.text]["mem_idx"] - 1)
                                return

                    error(f"`{token.text}` is not built-in", token.loc); exit(1)

            case TokenType.CMACRO:
                self.add_op(OpType.CMACRO, token, token.text)

            case _:
                self.new_method(token)

    def new_method(self, token):
        assert False, f"Unsupported TokenType.{token.type.name} in Parser.make_op()"

    def parse(self) -> tuple[list[Op], dict[str, dict], dict[str, dict]]:
        while not self.is_at_end():
            self.make_op()

        loc = self.tokens[-1].loc.copy()
        loc.col += len(self.tokens[-1].text)
        self.add_op(OpType.EOF, Token(None, "", loc))
        return (self.ops, self.mems, self.procs)