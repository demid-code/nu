import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Loc:
    filepath: Path
    line: int
    col: int

    def copy(self) -> object:
        return Loc(self.filepath, self.line, self.col)

    def __repr__(self) -> str:
        return f"{self.filepath}:{self.line}:{self.col}"

def report_error(msg: str, loc: Loc = None):
    formatted_msg = msg[0].upper() + msg[1:]
    if loc: print(f"{loc}: Error: {formatted_msg}")
    else: print(f"Error: {formatted_msg}")
    sys.exit(1)