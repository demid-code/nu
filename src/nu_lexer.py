from pathlib import Path

from nu_error import Loc, error, note, exit
from nu_utils import read_file
from nu_tokens import TokenType, Token

class Lexer:
    def __init__(self, filepath: Path):
        if not filepath.exists():
            error(f"`{filepath}` does not exist"); exit(1)

        if str(filepath.name).split(".")[1] != "nu":
            error("expected file extension to be .nu"); exit(1)

        self.loc = Loc(filepath, 1, 0)
        self.source = read_file(filepath)
        self.tokens = []

        self.cmacros = {}

        self.start = 0
        self.current = 0

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    @staticmethod
    def is_whitespace(char: str) -> bool:
        return char in (" ", "\n", "\t", "\r")

    def peek(self, ahead: int = 0) -> str:
        if self.current + ahead >= len(self.source): return "\0"
        return self.source[self.current + ahead]

    def match(self, char: str) -> bool:
        if self.peek() == char:
            self.advance()
            return True
        
        return False

    def add_token(self, token_type: TokenType, text: str = None):
        t = text or self.source[self.start:self.current]
        self.tokens.append(Token(token_type, t, self.loc.copy()))

    def skip_comment(self):
        if self.match("/"):
            while not self.is_at_end() and self.peek() != "\n":
                self.advance()
        else:
            self.add_token(TokenType.WORD)

    def lex_word(self):
        while not self.is_at_end() and not self.is_whitespace(self.peek()):
            self.advance()

        return self.source[self.start:self.current]

    def skip_whitespace(self):
        while self.is_whitespace(self.peek()):
            self.advance()

    def make_word(self):
        word = self.lex_word()

        if word == "cmacro":
            cmacro_loc = self.loc.copy()

            self.skip_whitespace()
            if self.is_at_end():
                error("expected cmacro name", self.loc); exit(1)

            self.start = self.current
            cmacro_name = self.lex_word()
            
            found_end = False

            self.start = self.current
            while True:
                if self.source[self.current:self.current+9] == "endcmacro":
                    found_end = True
                    break

                self.advance()

            if not found_end:
                error("cmacro was never closed", cmacro_loc); exit(1)

            self.cmacros[cmacro_name] = {"body": self.source[self.start:self.current]}
            self.current += 9
            self.start = self.current

            return
        elif word in self.cmacros:
            self.add_token(TokenType.CMACRO, self.cmacros[word]["body"])
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

    def make_char(self):
        while not self.is_at_end() and self.peek() != "'":
            if self.peek() == "\n":
                error("chars can't be multi-line", self.loc); exit(1)
            self.advance()

        if self.is_at_end():
            error("char was never closed", self.loc); exit(1)
        
        self.advance()

        og_char = self.source[self.start + 1:self.current - 1]
        real_char = og_char.encode().decode("unicode_escape")
        if len(real_char) != 1:
            error("char should have exactly one character length", self.loc)
            note("use strings if you need multiple characters together", self.loc)
            exit(1)

        self.add_token(TokenType.CHAR, og_char)

    def make_string(self):
        while not self.is_at_end() and self.peek() != "\"":
            if self.peek() == "\n": self.loc.line += 1
            self.advance()

        if self.is_at_end():
            error("string was never closed", self.loc); exit(1)
        
        self.advance()

        og_str = self.source[self.start + 1:self.current - 1]
        encoded_str = og_str.encode().decode("unicode_escape").encode("unicode_escape").decode()

        self.add_token(TokenType.STRING, encoded_str)

    def make_token(self):
        char = self.advance()

        match char:
            case _ if self.is_whitespace(char):
                if char == "\n":
                    self.loc.line += 1
                    self.loc.col = 0
            case _ if char == "/": self.skip_comment()
            case "\"": self.make_string()
            case "'": self.make_char()
            case _ if char == "-":
                if self.peek().isdigit(): self.make_number()
                else: self.add_token(TokenType.WORD)
            case _ if char.isdigit(): self.make_number()
            case _: self.make_word()

    def lex(self) -> list[Token]:
        while not self.is_at_end():
            self.loc.col += self.current - self.start
            self.start = self.current
            self.make_token()

        return self.tokens