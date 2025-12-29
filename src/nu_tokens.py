from enum import IntEnum, auto
from dataclasses import dataclass

from nu_error import Loc

class TokenType(IntEnum):
    WORD = auto()
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    STRING = auto()

@dataclass
class Token:
    type: TokenType
    text: str
    loc: Loc

    def __repr__(self) -> str:
        return f"{self.type.name}: {self.text}"