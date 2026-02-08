from pathlib import Path

from nu_error import error, exit
from nu_tokens import TokenType, Token
from nu_lexer import Lexer

class PreParser:
    def __init__(self, tokens: list[Token], paths: list[Path] = [], included_paths: list[Path] = []):
        self.tokens = tokens
        self.current = 0

        self.paths = paths
        self.included_paths = included_paths

        self.macros = {}

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
    
    def advance(self) -> tuple[Token, int]:
        idx = self.current
        self.current += 1
        return (self.tokens[idx], idx)

    def peek(self, ahead: int = 0) -> tuple[Token, int]:
        idx = self.current + ahead
        return (self.tokens[idx], idx)

    def parse_macro_definition(self):
        token, token_idx = self.peek(-1)

        if self.is_at_end():
            error("expected macro name", token.loc); exit(1)

        name, name_idx = self.advance()
        if name.type != TokenType.WORD:
            error("expected macro name to be a valid word", name.loc); exit(1)

        found_end = False

        while not self.is_at_end():
            tok, tok_idx = self.advance()

            if tok.type == TokenType.WORD:
                if tok.text == "macro":
                    error("can't define macro inside macro", tok.loc); exit(1)

                if tok.text == "endmacro":
                    found_end = True
                    break

        if not found_end:
            error("macro was never closed with `endmacro`", token.loc); exit(1)

        self.macros[name.text] = {"body": self.tokens[token_idx+2:self.current-1]}
        self.tokens[token_idx:self.current] = []
        self.current = token_idx

    def insert_macro(self):
        token, token_idx = self.peek(-1)
        self.tokens[token_idx:token_idx+1] = self.macros[token.text]["body"]
        self.current = token_idx

    def parse_include(self):
        token, token_idx = self.peek(-1)

        if self.is_at_end():
            error("expected filepath to include", token.loc); exit(1)

        path_token, path_idx = self.advance()
        if path_token.type != TokenType.STRING:
            error("filepath should be a string", path_token.loc); exit(1)

        path = Path(path_token.text)

        for p in self.paths:
            final_path = p.joinpath(path).resolve()
            if not final_path.exists(): continue
            if final_path in self.included_paths: continue

            included_tokens = Lexer(final_path).lex()

            pre_parser = PreParser(included_tokens, self.paths, self.included_paths)
            included_tokens = pre_parser.pre_parse()

            self.macros.update(pre_parser.macros)

            self.tokens[token_idx:path_idx+1] = included_tokens
            self.current = token_idx

            self.included_paths.append(final_path)

            return
        
        self.tokens[token_idx:path_idx+1] = []
        self.current = token_idx

    def scan_token(self):
        token, token_idx = self.advance()

        if token.type == TokenType.WORD:
            if token.text == "macro":     self.parse_macro_definition()
            if token.text in self.macros: self.insert_macro()

            if token.text == "include": self.parse_include()

    def pre_parse(self) -> list[Token]:
        while not self.is_at_end():
            self.scan_token()

        return self.tokens