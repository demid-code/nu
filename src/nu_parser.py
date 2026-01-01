from nu_error import report_error
from nu_tokens import TokenType, Token
from nu_ops import OpType, Op, WORD_TO_OP

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

        self.procs = []

        self.bind_name_stack = []

        self.ops = []

    def is_at_end(self, index: int = None) -> bool:
        i = index
        if i == None: i = self.current
        return i >= len(self.tokens)
    
    def advance(self) -> tuple[Token, int]:
        idx = self.current
        self.current += 1
        return (self.tokens[idx], idx)

    def add_op(self, op_type: OpType, token: Token, operand: any = None):
        self.ops.append(Op(op_type, token, operand))

    def make_op(self):
        token, token_idx = self.advance()

        match token.type:
            case TokenType.INT:
                self.add_op(OpType.PUSH_INT, token, int(token.text))

            case TokenType.FLOAT:
                self.add_op(OpType.PUSH_FLOAT, token, float(token.text))

            case TokenType.CHAR:
                char = token.text[1:-1].encode().decode("unicode_escape")
                self.add_op(OpType.PUSH_INT, token, ord(char))

            case TokenType.STRING:
                self.add_op(OpType.PUSH_CSTRING, token, token.text[1:-1].encode().decode("unicode_escape"))

            case TokenType.WORD:
                if token.text == "proc":
                    if self.is_at_end():
                        report_error("Expected procedure name", token.loc)

                    name = self.tokens[token_idx + 1]
                    if name.type != TokenType.WORD:
                        report_error("Expected procedure name to be a valid word", name.loc)

                    if self.is_at_end(token_idx + 1):
                        report_error("Expected `in` after procedure name", name.loc)

                    in_token = self.tokens[token_idx + 2]
                    if not (in_token.type == TokenType.WORD and in_token.text == "in"):
                        report_error("Expected `in` after procedure name", name.loc)

                    self.procs.append(name.text)

                if token.text == "let":
                    names = []
    
                    found_in = False
                    while not self.is_at_end():
                        tok, tok_idx = self.advance()

                        if tok.type == TokenType.WORD:
                            if tok.text == "in":
                                found_in = True
                                break
                            else: names.append(tok.text)

                    if len(names) <= 0: report_error("Expected bind names after `let`", token.loc)
                    self.bind_name_stack.append(names)

                    if not found_in:
                        report_error("Expected `in` after bind names", self.tokens[idx-1].loc)

                    self.add_op(OpType.LET, token, len(names))
                    self.add_op(OpType.IN, self.tokens[self.current-1])

                    return

                if token.text == "endlet":
                    names = self.bind_name_stack.pop()
                    self.add_op(OpType.ENDLET, token, len(names))
                    return

                if token.text in WORD_TO_OP:
                    self.add_op(WORD_TO_OP.get(token.text), token)
                elif token.text in self.procs:
                    self.add_op(OpType.CALL, token)
                else:
                    found = False
                    for name_list in self.bind_name_stack:
                        if token.text in name_list:
                            found = True

                            idx = name_list.index(token.text)
                            self.add_op(OpType.PUSH_BINDED, token, idx)

                    if not found:
                        report_error(f"`{token.text}` is not built-in", token.loc)

            case TokenType.CMACRO:
                self.add_op(OpType.CMACRO, token, None)

            case _:
                assert False, f"Unsupported TokenType.{token.type.name} in Parser.make_op()"

    def parse(self) -> list[Op]:
        while not self.is_at_end():
            self.make_op()
        
        self.add_op(OpType.EOF, None)

        return self.ops