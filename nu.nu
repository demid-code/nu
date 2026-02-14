include "std/std.nu"
include "std/string.nu"

// Token

const TOKEN_TYPE_WORD reset    endconst
const TOKEN_TYPE_INT  1 offset endconst

proc token_type_to_str // int -> str len
    let type in
        type      TOKEN_TYPE_WORD == if "WORD"
        else type TOKEN_TYPE_INT  == if "INT"
        endif endif
    endlet
endproc

const Token.type    reset              endconst
const Token.text    sizeof(int) offset endconst
const sizeof(Token) sizeof(Str) offset endconst

macro @Token.type Token.type + @int endmacro
macro @Token.text Token.text + @Str endmacro

macro !Token.type Token.type + !int endmacro
macro !Token.text Token.text + !Str endmacro

proc @Token // token -> type text textlen
    let token in
        token @Token.type
        token @Token.text
    endlet
endproc

proc !Token // type text textlen token
    let type text textlen token in
        type token !Token.type
        text textlen token !Token.text
    endlet
endproc

proc print_token // type text textlen
    let type text textlen in
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

// TODO: handle buffer overflow and realloc array
proc token_array_push // token_type token_text token_array
    let type text textlen token_array in
        type text textlen
        token_array @TokenArray.data token_array @TokenArray.size sizeof(Token) * +
        !Token
        token_array @TokenArray.size 1 + token_array !TokenArray.size
    endlet
endproc

// TODO: handle wrong indexing
proc token_array_get // index token_array -> type text textlen
    let index token_array in
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
const Lexer.start   sizeof(Str)        offset endconst
const Lexer.current sizeof(int)        offset endconst
const Lexer.tokens  sizeof(int)        offset endconst
const sizeof(Lexer) sizeof(TokenArray) offset endconst

macro @Lexer.src     Lexer.src     + @Str endmacro
macro @Lexer.start   Lexer.start   + @int endmacro
macro @Lexer.current Lexer.current + @int endmacro

macro !Lexer.src     Lexer.src     + !Str endmacro
macro !Lexer.start   Lexer.start   + !int endmacro
macro !Lexer.current Lexer.current + !int endmacro

proc lexer_init // lexer src(str len)
    let lexer src srclen in
        src srclen lexer !Lexer.src
        0 lexer !Lexer.start
        0 lexer !Lexer.current
        lexer Lexer.tokens + token_array_init
    endlet
endproc

proc lexer_free // lexer
    let lexer in
        lexer Lexer.tokens + token_array_free
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

proc lexer_advance // lexer -> char
    let lexer in
        lexer lexer_peek
        lexer @Lexer.current 1 + lexer !Lexer.current
    endlet
endproc

proc lexer_skip_whitespace // lexer
    let lexer in
        while lexer lexer_is_at_end not lexer lexer_peek is_whitespace and do
            lexer lexer_advance
        endwhile
    endlet
endproc

proc lexer_make_word // lexer
    let lexer in
        while lexer lexer_is_at_end not lexer lexer_peek is_whitespace not and do
            lexer lexer_advance
        endwhile

        TOKEN_TYPE_WORD
        lexer @Lexer.src drop
        lexer @Lexer.start sizeof(char) * +
        lexer @Lexer.current lexer @Lexer.start -
        lexer Lexer.tokens + token_array_push
    endlet
endproc

proc lexer_make_token // lexer
    let lexer in
        lexer lexer_make_word
    endlet
endproc

proc lexer_lex // lexer
    let lexer in
        lexer lexer_skip_whitespace
        
        while lexer lexer_is_at_end not do
            lexer @Lexer.current lexer !Lexer.start
            lexer lexer_make_token
            lexer lexer_skip_whitespace
        endwhile
    endlet
endproc

proc main
    mem lexer sizeof(Lexer) endmem

    lexer "10 10 + print\n" lexer_init
    lexer lexer_lex

    lexer Lexer.tokens + token_array_print
    
    lexer lexer_free
endproc main