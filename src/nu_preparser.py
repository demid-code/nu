from nu_error import report_error
from nu_tokens import TokenType, Token

class PreParser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

        self.macros = {}

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
    
    def peek(self, ahead: int = 0) -> tuple[Token, int]:
        idx = self.current + ahead
        assert idx < len(self.tokens)
        return (self.tokens[idx], idx)

    def advance(self) -> tuple[Token, int]:
        idx = self.current
        self.current += 1
        return (self.tokens[idx], idx)

    def parse_macro(self):
        macro, macro_idx = self.peek(-1)

        if self.is_at_end():
            report_error("Expected name of macro", macro.loc)

        name, name_idx = self.advance()
        if name.type != TokenType.WORD:
            report_error("Expected name of macro to be a valid word", name.loc)

        found_end = False
        while not self.is_at_end():
            tok, tok_idx = self.advance()
            if tok.type == TokenType.WORD:
                if tok.text == "macro":
                    report_error("You can't nest macros", tok.loc)
                
                if tok.text == "endmacro":
                    found_end = True
                    break

        if not found_end:
            report_error("Expected `endmacro` to close macro", macro.loc)

        self.macros[name.text] = {"body": self.tokens[name_idx+1:self.current-1]}
        self.tokens[macro_idx:self.current] = []
        self.current -= self.current - macro_idx

    def replace_with_macro(self):
        token, token_idx = self.peek(-1)

        self.tokens[token_idx:token_idx+1] = self.macros[token.text]["body"]
        self.current = token_idx

    def scan_token(self):
        token, token_idx = self.advance()

        if token.type == TokenType.WORD:
            if token.text == "macro": self.parse_macro()
            if token.text in self.macros: self.replace_with_macro()

    def pre_parse(self) -> list[Token]:
        while not self.is_at_end():
            self.scan_token()
        
        return self.tokens