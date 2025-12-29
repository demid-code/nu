import subprocess
from pathlib import Path

from nu_error import report_error

def read_file(filepath: Path | str) -> str:
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        report_error(str(e))

def write_file(filepath: Path | str, content: str):
    try:
        with open(filepath, "w") as f:
            return f.write(content)
    except Exception as e:
        report_error(str(e))

def cmd_call(cmd: list[str], silent: bool = False):
    assert type(cmd) == list
    
    formatted_cmd = [str(x) for x in cmd]
    if not silent:
        print(f"CMD: {" ".join(formatted_cmd)}")
    
    subprocess.run(formatted_cmd)