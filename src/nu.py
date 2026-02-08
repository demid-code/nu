import shutil, os
from sys import argv
from pathlib import Path

from nu_error import error, exit
from nu_utils import write_file, cmd_call
from nu_lexer import Lexer
from nu_preparser import PreParser
from nu_parser import Parser
from nu_linker import Linker
from nu_compiler import Compiler

def usage():
    print(f"Usage: {argv[0]} <command>")
    print("Commands:")
    print("    help                Prints usage")
    print("    lex   <filepath>    Produces tokens and prints them")
    print("    parse <filepath>    Produces ops and prints them")
    print("    com   <filepath>    Compiles program")
    print()
    print("Flags:")
    print("    -r --run       Run after successfull compilation")
    print("    -s --silent    Silent mode")
    print()

def main():
    if len(argv) < 2:
        usage()
        error("no command is provided"); exit(1)

    command = argv[1]

    match command:
        case "help":
            usage(); return

        case "lex" | "parse" | "com":
            if len(argv) < 3:
                error(f"expected <filepath> for `{command}` command"); exit(1)

            nu_path = Path(__file__).parent.parent

            filepath = Path(argv[2])
            filename = filepath.name.split(".")[0]
            
            lexer = Lexer(filepath)
            tokens = lexer.lex()
            if len(tokens) == 0: return

            if command == "lex":
                for token in tokens:
                    print(token)
                return
            
            pre_parser = PreParser(tokens, [nu_path, filepath.parent], [filepath.resolve()])
            tokens = pre_parser.pre_parse()
            if len(tokens) == 0: return
            
            parser = Parser(tokens)
            ops = parser.parse()
            if len(ops) == 0: return

            linker = Linker(ops)
            ops = linker.link()
            if len(ops) == 0: return

            if command == "parse":
                for i, op in enumerate(ops):
                    print(f"{i}: {op}")
                return
            
            silent_mode = ("-s" in argv) or ("--silent" in argv)
            
            build_path = filepath.parent.joinpath("build")
            build_path.mkdir(exist_ok=True)

            runtime_h_path = nu_path.joinpath("runtime/nu_runtime.h")
            runtime_c_path = nu_path.joinpath("runtime/nu_runtime.c")

            build_runtime_h_path = build_path.joinpath("nu_runtime.h")
            build_runtime_c_path = build_path.joinpath("nu_runtime.c")

            shutil.copyfile(runtime_h_path, build_runtime_h_path)
            shutil.copyfile(runtime_c_path, build_runtime_c_path)

            c_path = build_path.joinpath("main.c")
            exe_name = build_path.joinpath(f"{filename}.exe") if os.name == "nt" else build_path.joinpath(filename)

            compiler = Compiler(ops)
            output = compiler.compile()

            write_file(c_path, output)

            cmd_call(["gcc", "-o", exe_name, c_path, build_runtime_c_path], silent_mode)

            if ("-r" in argv) or ("--run" in argv):
                cmd_call([exe_name], silent_mode)

        case _:
            usage()
            error(f"`{command}` is invalid command"); exit(1)

if __name__ == "__main__":
    main()