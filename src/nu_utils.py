import subprocess
from pathlib import Path
from nu_error import error, exit

def read_file(filepath: str | Path) -> str:
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        error(str(e)); exit(1)

def write_file(filepath: str | Path, content: str):
    try:
        with open(filepath, "w") as f:
            return f.write(content)
    except Exception as e:
        error(str(e)); exit(1)

def cmd_call(cmd: list[str], silent: bool = False):
    assert type(cmd) == list
    str_cmd = [str(x) for x in cmd]
    
    if not silent:
        print(f"CMD: {" ".join(str_cmd)}")

    subprocess.call(str_cmd)