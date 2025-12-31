import sys, shutil, os
from pathlib import Path

from nu_error import report_error
from nu_utils import write_file, cmd_call
from nu_lexer import Lexer
from nu_preparser import PreParser
from nu_parser import Parser
from nu_compiler import Compiler

def usage():
    print(f"Usage: {sys.argv[0]} <command> [flags]")
    print("Commands:")
    print("    help                Prints usage")
    print("    lex   <filepath>    Generates tokens from source and prints them out")
    print("    parse <filepath>    Generates ops from source and prints them out")
    print("    gen   <filepath>    Generates build folder from source")
    print("    com   <filepath>    Compiles build folder")
    print()
    print("Flags:")
    print("    -r    Runs program after successfull compilation")
    print()

def main():
    if len(sys.argv) < 2:
        usage()
        report_error("no command is provided")

    command = sys.argv[1]

    match command:
        case "help":
            usage()
            return
        
        case "lex" | "parse" | "gen" | "com":
            if len(sys.argv) < 3:
                report_error(f"expected <filepath> for `{command}` command")

            nu_path = Path(__file__).resolve().parent.parent
            filepath = Path(sys.argv[2]).resolve()
            filename = str(filepath.name).split(".")[0]
            
            lexer = Lexer(filepath)
            tokens = lexer.lex()
            if len(tokens) <= 0: return

            if command == "lex":
                for token in tokens:
                    print(token)
                return
            
            pre_parser = PreParser(tokens)
            tokens = pre_parser.pre_parse()
            if len(tokens) <= 0: return

            parser = Parser(tokens)
            ops = parser.parse()
            if len(ops) <= 0: return

            if command == "parse":
                for i, op in enumerate(ops):
                    print(f"{i}: {op}")
                return
            
            runtime_path = nu_path.joinpath("runtime")
            runtime_h = runtime_path.joinpath("nu_runtime.h")
            runtime_c = runtime_path.joinpath("nu_runtime.c")

            build_path = filepath.parent.joinpath("build")
            build_path.mkdir(exist_ok=True)

            build_runtime_h = build_path.joinpath("nu_runtime.h")
            build_runtime_c = build_path.joinpath("nu_runtime.c")

            shutil.copy(runtime_h, build_runtime_h)
            shutil.copy(runtime_c, build_runtime_c)

            main_c_path = build_path.joinpath("main.c")
            
            compiler = Compiler(ops)
            output = compiler.compile()

            write_file(main_c_path, output)

            if command == "gen": return

            silent_mode = "-s" in sys.argv

            exe_path = build_path.joinpath(f"{filename}.exe") if os.name == "nt" else build_path.joinpath(f"{filename}")

            cmd_call(["gcc", "-o", exe_path, main_c_path, build_runtime_c], silent_mode)

            if "-r" in sys.argv:
                cmd_call([exe_path], silent_mode)

        case _:
            usage()
            report_error(f"`{command}` command does not exist")

if __name__ == "__main__":
    main()