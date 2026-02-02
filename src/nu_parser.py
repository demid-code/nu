from nu_error import Loc, error, exit
from nu_tokens import TokenType, Token
from nu_ops import OpType, WORD_TO_OPTYPE, Op

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

        self.ops = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def advance(self) -> Token:
        self.current += 1
        return self.tokens[self.current - 1]

    def add_op(self, op_type: OpType, token: Token, operand: any = None):
        self.ops.append(Op(op_type, token, operand))

    def make_op(self):
        token = self.advance()

        match token.type:
            case TokenType.INT:
                self.add_op(OpType.PUSH_INT, token, token.text)

            case TokenType.FLOAT:
                self.add_op(OpType.PUSH_FLOAT, token, token.text)

            case TokenType.CHAR:
                char = token.text.encode().decode("unicode_escape")
                self.add_op(OpType.PUSH_INT, token, str(ord(char)))

            case TokenType.WORD:
                if token.text in WORD_TO_OPTYPE:
                    self.add_op(WORD_TO_OPTYPE.get(token.text), token)
                else:
                    error(f"`{token.text}` is not built-in", token.loc); exit(1)

            case _:
                self.new_method(token)

    def new_method(self, token):
        assert False, f"Unsupported TokenType.{token.type.name} in Parser.make_op()"

    def parse(self) -> list[Op]:
        while not self.is_at_end():
            self.make_op()

        loc = self.tokens[-1].loc.copy()
        loc.col += len(self.tokens[-1].text)
        self.add_op(OpType.EOF, Token(None, "", loc))
        return self.ops