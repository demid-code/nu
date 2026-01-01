from nu_error import report_error
from nu_tokens import TokenType, Token
from nu_ops import OpType, Op, WORD_TO_OP

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

        self.procs = []

        self.ops = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
    
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

                    if token_idx + 1 >= len(self.tokens):
                        report_error("Expected `in` after procedure name", name.loc)

                    in_token = self.tokens[token_idx + 2]
                    if not (in_token.type == TokenType.WORD and in_token.text == "in"):
                        report_error("Expected `in` after procedure name", name.loc)

                    self.procs.append(name.text)

                if token.text in WORD_TO_OP:
                    self.add_op(WORD_TO_OP.get(token.text), token)
                elif token.text in self.procs:
                    self.add_op(OpType.CALL, token)
                else:
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