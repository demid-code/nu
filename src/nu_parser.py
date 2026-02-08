from nu_error import Loc, error, exit
from nu_tokens import TokenType, Token
from nu_ops import OpType, WORD_TO_OPTYPE, Op
from nu_evaluator import Evaluator

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

        self.ops = []

        self.mems = {}

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

                    mem_size = Evaluator(self.tokens[name_idx+1:self.current-1]).evaluate()[0]
                    self.mems[name.text] = {"size": mem_size}
                elif token.text in self.mems:
                    self.add_op(OpType.PUSH_MEM, token)
                elif token.text in WORD_TO_OPTYPE:
                    self.add_op(WORD_TO_OPTYPE.get(token.text), token)
                else:
                    error(f"`{token.text}` is not built-in", token.loc); exit(1)

            case TokenType.CMACRO:
                self.add_op(OpType.CMACRO, token, token.text)

            case _:
                self.new_method(token)

    def new_method(self, token):
        assert False, f"Unsupported TokenType.{token.type.name} in Parser.make_op()"

    def parse(self) -> tuple[list[Op], dict[str, dict]]:
        while not self.is_at_end():
            self.make_op()

        loc = self.tokens[-1].loc.copy()
        loc.col += len(self.tokens[-1].text)
        self.add_op(OpType.EOF, Token(None, "", loc))
        return (self.ops, self.mems)