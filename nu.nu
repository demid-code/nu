include "std/std.nu"
include "std/string.nu"

// Loc

const Loc.filepath reset              endconst
const Loc.line     sizeof(Str) offset endconst
const Loc.col      sizeof(int) offset endconst
const sizeof(Loc)  sizeof(int) offset endconst

macro @Loc.filepath Loc.filepath + @Str endmacro
macro @Loc.line     Loc.line     + @int endmacro
macro @Loc.col      Loc.col      + @int endmacro

macro !Loc.filepath Loc.filepath + !Str endmacro
macro !Loc.line     Loc.line     + !int endmacro
macro !Loc.col      Loc.col      + !int endmacro

proc @Loc // Loc -> filepath filepathlen line col
    let loc in
        loc @Loc.filepath
        loc @Loc.line
        loc @Loc.col
    endlet
endproc

proc !Loc // filepath filepathlen line col Loc
    let filepath filepathlen line col loc in
        filepath filepathlen loc !Loc.filepath
        line loc !Loc.line
        col loc !Loc.col
    endlet
endproc

proc fputloc // file Loc
    let file filepath filepathlen line col in
        file filepath filepathlen fputs
        file ':' fputc
        file line fputd
        file ':' fputc
        file col fputd
    endlet
endproc

macro putloc
    stdout 4 roll 4 roll 4 roll 4 roll fputloc
endmacro

macro eputloc
    stderr stdout 4 roll 4 roll 4 roll 4 roll fputloc
endmacro

// Token

const TOKEN_TYPE_WORD   reset    endconst
const TOKEN_TYPE_INT    1 offset endconst
const TOKEN_TYPE_FLOAT  1 offset endconst

proc token_type_to_str // int -> str len
    let type in
        type      TOKEN_TYPE_WORD   == if "WORD"
        else type TOKEN_TYPE_INT    == if "INT"
        else type TOKEN_TYPE_FLOAT  == if "FLOAT"
        endif endif endif
    endlet
endproc

const Token.type    reset              endconst
const Token.text    sizeof(int) offset endconst
const Token.loc     sizeof(Str) offset endconst
const sizeof(Token) sizeof(Loc) offset endconst

macro @Token.type Token.type + @int endmacro
macro @Token.text Token.text + @Str endmacro
macro @Token.loc  Token.loc  + @Loc endmacro

macro !Token.type Token.type + !int endmacro
macro !Token.text Token.text + !Str endmacro
macro !Token.loc  Token.loc  + !Loc endmacro

proc @Token // token -> type text loc
    let token in
        token @Token.type
        token @Token.text
        token @Token.loc
    endlet
endproc

proc !Token // type text textlen filepath filepathlen line col token
    let type text textlen filepath filepathlen line col token in
        type token !Token.type
        text textlen token !Token.text
        filepath filepathlen line col token !Token.loc
    endlet
endproc

proc print_token // type text textlen filepath filepathlen line col
    let type text textlen filepath filepathlen line col in
        filepath filepathlen line col putloc ": " puts
        type token_type_to_str puts
        ": `" puts
        text textlen puts "`\n" puts
    endlet
endproc

// TokenArray

const TokenArray.data     reset              endconst
const TokenArray.capacity sizeof(ptr) offset endconst
const TokenArray.size     sizeof(int) offset endconst
const sizeof(TokenArray)  sizeof(int) offset endconst

macro @TokenArray.data     TokenArray.data     + @ptr endmacro
macro @TokenArray.capacity TokenArray.capacity + @int endmacro
macro @TokenArray.size     TokenArray.size     + @int endmacro

macro !TokenArray.data     TokenArray.data     + !ptr endmacro
macro !TokenArray.capacity TokenArray.capacity + !int endmacro
macro !TokenArray.size     TokenArray.size     + !int endmacro

proc token_array_init // token_array
    let token_array in
        8 token_array !TokenArray.capacity
        0 token_array !TokenArray.size
        token_array @TokenArray.capacity sizeof(Token) * malloc token_array !TokenArray.data
    endlet
endproc

proc token_array_free // token_array
    let token_array in
        token_array @TokenArray.data free
    endlet
endproc

proc token_array_push // token_type token_text token_loc token_array
    let type text textlen filepath filepathlen line col token_array in
        token_array @TokenArray.size token_array @TokenArray.capacity >= if
            token_array @TokenArray.capacity 2 * token_array !TokenArray.capacity // increase capacity

            // realloc array data
            token_array @TokenArray.capacity sizeof(Token) * token_array @TokenArray.data realloc
            token_array !TokenArray.data
        endif

        type text textlen filepath filepathlen line col
        token_array @TokenArray.data token_array @TokenArray.size sizeof(Token) * +
        !Token
        token_array @TokenArray.size 1 + token_array !TokenArray.size
    endlet
endproc

proc token_array_get // index token_array -> type text textlen filepath filepathlen line col
    let index token_array in
        index 0 < index token_array @TokenArray.size >= or if
            "Error: Invalid index in token_array_get\n" eputs
            -1 exit
        endif

        token_array @TokenArray.data index sizeof(Token) * + @Token
    endlet
endproc

proc token_array_print // token_array
    let token_array in
        0 while dup token_array @TokenArray.size < do
            dup token_array token_array_get print_token
            1 +
        endwhile drop
    endlet
endproc

// Lexer

const Lexer.src     reset                     endconst
const Lexer.loc     sizeof(Str)        offset endconst
const Lexer.start   sizeof(Loc)        offset endconst
const Lexer.current sizeof(int)        offset endconst
const Lexer.tokens  sizeof(int)        offset endconst
const sizeof(Lexer) sizeof(TokenArray) offset endconst

macro @Lexer.src     Lexer.src     + @Str endmacro
macro @Lexer.start   Lexer.start   + @int endmacro
macro @Lexer.current Lexer.current + @int endmacro
macro @Lexer.loc     Lexer.loc     + @Loc endmacro

macro !Lexer.src     Lexer.src     + !Str endmacro
macro !Lexer.loc     Lexer.loc     + !Loc endmacro
macro !Lexer.start   Lexer.start   + !int endmacro
macro !Lexer.current Lexer.current + !int endmacro

proc lexer_init // filepath(str len) src(str len) lexer
    let filepath filepathlen src srclen lexer in
        src srclen lexer !Lexer.src
        filepath filepathlen 1 1 lexer !Lexer.loc
        0 lexer !Lexer.start
        0 lexer !Lexer.current
        lexer Lexer.tokens + token_array_init
    endlet
endproc

proc lexer_free // lexer
    let lexer in
        lexer Lexer.tokens + token_array_free
        lexer @Lexer.src drop free
    endlet
endproc

proc lexer_is_at_end // lexer -> bool
    let lexer in
        lexer @Lexer.current
        lexer @Lexer.src swap drop >=
    endlet
endproc

proc lexer_peek // lexer -> char
    let lexer in
        lexer @Lexer.src drop
        lexer @Lexer.current sizeof(char) * + @char
    endlet
endproc

proc lexer_peek_ahead // offset lexer -> char
    let offset lexer in
        lexer @Lexer.src drop
        lexer @Lexer.current offset + sizeof(char) * + @char
    endlet
endproc

proc lexer_advance // lexer -> char
    let lexer in
        lexer lexer_peek
        lexer @Lexer.current 1 + lexer !Lexer.current
    endlet
endproc

proc lexer_match // char lexer -> bool
    let char lexer in
        lexer lexer_peek char == if
            lexer lexer_advance drop true
        else
            false
        endif
    endlet
endproc

proc lexer_skip_whitespace // lexer
    let lexer in
        while lexer lexer_is_at_end not lexer lexer_peek is_whitespace and do
            lexer lexer_peek '\n' == if
                lexer @Lexer.loc drop 1 + 0 lexer !Lexer.loc
            endif

            lexer lexer_advance
        endwhile
    endlet
endproc

proc lexer_get_current_str // lexer -> str strlen
    let lexer in
        lexer @Lexer.src drop
        lexer @Lexer.start sizeof(char) * +
        lexer @Lexer.current lexer @Lexer.start -
    endlet
endproc

proc lexer_add_token // type lexer
    let type lexer in
        type
        lexer lexer_get_current_str
        lexer @Lexer.loc
        lexer Lexer.tokens + token_array_push
    endlet
endproc

proc lexer_skip_comment // lexer
    let lexer in
        '/' lexer lexer_match if
            while lexer lexer_is_at_end not lexer lexer_peek '\n' == not and do
                lexer lexer_advance
            endwhile
        else
            TOKEN_TYPE_WORD lexer lexer_add_token
        endif
    endlet
endproc

proc lexer_make_word // lexer
    let lexer in
        while lexer lexer_is_at_end not lexer lexer_peek is_whitespace not and do
            lexer lexer_advance
        endwhile

        TOKEN_TYPE_WORD lexer lexer_add_token
    endlet
endproc

proc lexer_make_number // lexer
    mem is_float sizeof(bool) endmem
    false is_float !bool

    let lexer in
        while lexer lexer_is_at_end not lexer lexer_peek is_digit and do
            lexer lexer_advance
        endwhile

        lexer lexer_peek '.' == 1 lexer lexer_peek_ahead is_digit and if
            true is_float !bool
            lexer lexer_advance

            while lexer lexer_is_at_end not lexer lexer_peek is_digit and do
                lexer lexer_advance
            endwhile
        endif

        is_float @bool if TOKEN_TYPE_FLOAT else TOKEN_TYPE_INT endif
        lexer lexer_add_token
    endlet
endproc

proc lexer_make_token // lexer
    let lexer in
        lexer lexer_advance
        
        let char in
            char is_digit if
                lexer lexer_make_number
            else char '/' == if
                lexer lexer_skip_comment
            else char '-' == 1 lexer lexer_peek_ahead is_digit and if
                lexer lexer_make_number
            else char is_whitespace if
                char '\n' == if
                    lexer @Lexer.loc drop 1 + 0 lexer !Lexer.loc
                endif
            else
                lexer lexer_make_word
            endif endif endif endif
        endlet
    endlet
endproc

proc lexer_lex // lexer
    let lexer in
        lexer lexer_skip_whitespace

        while lexer lexer_is_at_end not do
            lexer @Lexer.loc
            lexer @Lexer.current lexer @Lexer.start - +
            lexer !Lexer.loc
            lexer @Lexer.current lexer !Lexer.start
            lexer lexer_make_token
            // lexer lexer_skip_whitespace
        endwhile
    endlet
endproc

// Parser

const Parser.tokens  reset              endconst
const Parser.current sizeof(ptr) offset endconst
const sizeof(Parser) sizeof(int) offset endconst

macro @Parser.tokens  Parser.tokens  + @ptr endmacro // parser -> ptr
macro @Parser.current Parser.current + @int endmacro // parser -> int

macro !Parser.tokens  Parser.tokens  + !ptr endmacro // ptr parser
macro !Parser.current Parser.current + !int endmacro // int parser

proc parser_init // token_array parser
    let token_array parser in
        token_array parser !Parser.tokens
        0 parser !Parser.current
    endlet
endproc

proc parser_free // parser
    drop // implement later on if you allocate anything
endproc

proc parser_is_at_end // parser -> bool
    let parser in
        parser @Parser.current
        parser @Parser.tokens @TokenArray.size >=
    endlet
endproc

proc parser_peek // parser -> Token
    let parser in
        parser @Parser.tokens @TokenArray.data parser @Parser.current sizeof(Token) * + @Token
    endlet
endproc

proc parser_advance // parser -> Token
    let parser in
        parser parser_peek
        parser @Parser.current 1 + parser !Parser.current
    endlet
endproc

proc parser_make_op // parser
    let parser in
        parser parser_advance

        let type text textlen in
            type TOKEN_TYPE_WORD == if
                "parse word\n" puts
            else type TOKEN_TYPE_INT == if
                "parse int\n" puts
            else type TOKEN_TYPE_FLOAT == if
                "parse float\n" puts
            endif endif endif
        endlet
    endlet
endproc

proc parser_parse // parser
    let parser in
        while parser parser_is_at_end not do
            parser parser_make_op
        endwhile
    endlet
endproc

proc usage
    "Usage: " puts 0 argv dup cstrlen puts " <command>\n"       puts
    "Commands:\n"                                               puts
    "    help                Prints usage\n"                    puts
    "    lex   <filepath>    Produces tokens and prints them\n" puts
    "    parse <filepath>    Produces ops and prints them\n"    puts
    "\n"                                                        puts
endproc

proc main
    mem lexer  sizeof(Lexer)  endmem
    mem parser sizeof(Parser) endmem

    argc 2 < if
        usage
        "Error: No command is provided\n" eputs
        -1 exit
    endif

    1 argv
    let command in
        command "help" drop cstreq if
            usage
            0 exit
        else command "lex" drop cstreq command "parse" drop cstreq or if
            argc 3 < if
                "Error: Expected <filepath> for `" eputs command dup cstrlen eputs "` command\n" eputs
                -1 exit
            endif

            // lexing

            2 argv dup cstrlen over over read_file lexer lexer_init
            lexer lexer_lex

            command "lex" drop cstreq if
                lexer Lexer.tokens + token_array_print
                lexer lexer_free
                0 exit
            endif

            // parsing
            lexer Lexer.tokens + parser parser_init
            parser parser_parse

            // freeing
            parser parser_free
            lexer lexer_free
        else
            usage
            "Error: Invalid command `" eputs command dup cstrlen eputs "`\n" eputs
            -1 exit
        endif endif
    endlet
endproc main