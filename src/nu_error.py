import sys
from sys import exit
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Loc:
    filepath: Path
    line: int
    col: int

    def copy(self) -> Loc:
        return Loc(self.filepath, self.line, self.col)

    def __repr__(self) -> str:
        return f"{self.filepath}:{self.line}:{self.col}"

def error(msg: str, loc: Loc = None):
    formatted_msg = msg[0].upper() + msg[1:]
    if loc:
        print(f"{loc}: Error: {formatted_msg}", file=sys.stderr)
    else:
        print(f"Error: {formatted_msg}", file=sys.stderr)

def note(msg: str, loc: Loc = None):
    formatted_msg = msg[0].upper() + msg[1:]
    if loc:
        print(f"{loc}: Note: {formatted_msg}", file=sys.stderr)
    else:
        print(f"Note: {formatted_msg}", file=sys.stderr)