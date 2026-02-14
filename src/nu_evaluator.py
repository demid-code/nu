from nu_error import error, exit
from nu_tokens import TokenType, Token

class Evaluator:
    def __init__(self, tokens: list[Token], offset: int = 0, consts: dict[str, dict] = {}):
        self.tokens = tokens
        self.current = 0

        self.offset = offset
        self.consts = consts

        self.stack = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
    
    def advance(self) -> Token:
        self.current += 1
        return self.tokens[self.current - 1]

    def push(self, value: any):
        self.stack.append(value)

    def pop(self) -> any:
        return self.stack.pop()

    def scan_token(self):
        token = self.advance()

        match token.type:
            case TokenType.INT:
                self.push(int(token.text))

            case TokenType.WORD:
                if token.text == "+":
                    b = self.pop()
                    a = self.pop()
                    self.push(a + b)
                elif token.text == "reset":
                    self.offset = 0
                    self.push(self.offset)
                elif token.text == "offset":
                    val = self.pop()
                    self.offset += val
                    self.push(self.offset)
                elif token.text in self.consts:
                    self.push(self.consts[token.text]["value"])
                else:
                    error(f"`{token.text}` is unsupported operation in runtime evaluation", token.loc); exit(1)

            case _:
                assert False, f"Unsupported TokenType.{token.type.name} in Evaluator.scan_token()"

    def evaluate(self) -> list[any]:
        while not self.is_at_end():
            self.scan_token()

        return self.stack