from pathlib import Path

from nu_error import report_error
from nu_tokens import TokenType, Token
from nu_lexer import Lexer

class PreParser:
    def __init__(self, tokens: list[Token], include_paths: list[Path] = [], included_paths: list[Path] = []):
        self.tokens = tokens
        self.current = 0

        self.include_paths = include_paths
        self.included_paths = included_paths

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

    def parse_include(self):
        include, include_idx = self.peek(-1)

        if self.is_at_end():
            report_error("Expected path to include", include.loc)

        path_token, path_idx = self.advance()
        if path_token.type != TokenType.STRING:
            report_error("Expected path to be a string", path_token.loc)

        path = Path(path_token.text[1:-1].encode().decode("unicode_escape")).resolve()
        
        for include_path in self.include_paths:
            final_path = include_path.joinpath(path).resolve()

            if not final_path.exists():
                continue

            if final_path in self.included_paths:
                continue
            
            included_tokens = Lexer(final_path).lex()
            included_tokens, macros = PreParser(included_tokens, self.include_paths + [final_path.parent], self.included_paths + [final_path]).pre_parse()

            self.macros.update(macros)
            self.tokens[include_idx:path_idx+1] = included_tokens
            self.current = include_idx

            self.included_paths.append(final_path)

            return
        
        self.tokens[include_idx:path_idx+1] = []
        self.current = include_idx

    def scan_token(self):
        token, token_idx = self.advance()

        if token.type == TokenType.WORD:
            if token.text == "macro": self.parse_macro()
            if token.text in self.macros: self.replace_with_macro()

            if token.text == "include": self.parse_include()

    def pre_parse(self) -> tuple[list[Token], dict[str, dict]]:
        while not self.is_at_end():
            self.scan_token()
        
        return (self.tokens, self.macros)