from pathlib import Path

from nu_error import Loc, report_error
from nu_utils import read_file
from nu_tokens import TokenType, Token

class Lexer:
    def __init__(self, filepath: Path):
        if not filepath.exists():
            report_error(f"`{filepath}` does not exist")

        if str(filepath.name).split(".")[1] != "nu":
            report_error(f"`{filepath}` should have .nu extension")

        self.loc = Loc(filepath, 1, 1)
        self.source = read_file(filepath)

        self.tokens = []
        self.cmacros = {}

        self.start = 0
        self.current = 0

    def update_pos(self):
        self.loc.col += self.current - self.start
        self.start = self.current

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]
    
    def is_whitespace(self, char: str) -> bool:
        return char in (" ", "\n", "\r", "\t")

    def peek(self, ahead: int = 0) -> str:
        if self.current + ahead >= len(self.source): return "\0"
        return self.source[self.current + ahead]

    def match(self, char: str) -> bool:
        if self.peek() == char:
            self.advance()
            return True
        
        return False

    def match_str(self, string: str) -> bool:
        if self.current + len(string) > len(self.source): return False
        return self.source[self.current:self.current + len(string)] == string

    def add_token(self, token_type: TokenType, text: str = None):
        self.tokens.append(Token(token_type, text or self.source[self.start:self.current], self.loc.copy()))

    def skip_comment(self):
        if self.match("/"):
            while not self.is_at_end() and self.peek() != "\n":
                self.advance()
        else:
            self.add_token(TokenType.WORD)

    def skip_whitespace(self):
        while not self.is_at_end() and self.is_whitespace(self.peek()):
            if self.peek() == "\n":
                self.loc.line += 1
            self.advance()

    def lex_word(self) -> str:
        while not self.is_at_end() and not self.is_whitespace(self.peek()):
            self.advance()

        return self.source[self.start:self.current]

    def make_word(self):
        word = self.lex_word()

        if word == "cmacro":
            self.skip_whitespace()
            self.update_pos()

            name = self.lex_word()
            
            if name.strip() == "":
                report_error("Expected cmacro name", self.loc)

            self.skip_whitespace()
            self.update_pos()

            found_end = False
            while not self.is_at_end():
                if self.match_str("endcmacro"):
                    found_end = True
                    break
                if self.peek() == "\n":
                    self.loc.line += 1
                self.advance()

            # self.update_pos()
            if not found_end:
                report_error("Expected `endcmacro` to close cmacro", self.loc)

            body = self.source[self.start:self.current]
            self.cmacros[name] = body

            self.current += 9
            self.update_pos()

            return
        elif word in self.cmacros:
            self.add_token(TokenType.CMACRO, self.cmacros[word])
            
            return

        self.add_token(TokenType.WORD)

    def make_number(self):
        is_float = False
        while not self.is_at_end() and self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek(1).isdigit():
            is_float = True
            self.advance()

            while not self.is_at_end() and self.peek().isdigit():
                self.advance()

        self.add_token(TokenType.FLOAT if is_float else TokenType.INT)

    def make_string(self):
        while not self.is_at_end() and self.peek() != "\"":
            if self.peek() == "\n":
                self.loc.line += 1
            self.advance()

        self.advance()

        self.add_token(TokenType.STRING)

    def make_char(self):
        while not self.is_at_end() and self.peek() != "'":
            if self.peek() == "\n":
                report_error("chars can't be multi-line", self.loc)
            self.advance()

        self.advance()

        char = self.source[self.start:self.current][1:-1].encode().decode("unicode_escape")
        if len(char) > 1:
            report_error("char should be exactly 1 character long. Use strings instead", self.loc)

        self.add_token(TokenType.CHAR)

    def make_token(self):
        char = self.advance()

        match char:
            case _ if self.is_whitespace(char):
                if char == "\n":
                    self.loc.line += 1
                    self.loc.col = 0
            case "/": self.skip_comment()
            case "\"": self.make_string()
            case "'": self.make_char()
            case _ if char.isdigit(): self.make_number()
            case _: self.make_word()

    def lex(self) -> list[Token]:
        while not self.is_at_end():
            self.update_pos()
            self.make_token()

        return self.tokens