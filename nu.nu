include "std/std.nu"
include "std/string.nu"

// Lexer

const Lexer.src     reset              endconst
const Lexer.start   sizeof(Str) offset endconst
const Lexer.current sizeof(int) offset endconst
const sizeof(Lexer) sizeof(int) offset endconst

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
    endlet
endproc

proc lexer_free // lexer
    drop // todo implement later if you allocate something
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

        lexer @Lexer.src drop
        lexer @Lexer.start sizeof(char) * +
        lexer @Lexer.current lexer @Lexer.start - puts '\n' putc
    endlet
endproc

proc lexer_make_token // lexer
    let lexer in
        lexer lexer_make_word
    endlet
endproc

proc lexer_lex // lexer
    let lexer in
        while lexer lexer_is_at_end not do
            lexer lexer_skip_whitespace
            lexer @Lexer.current lexer !Lexer.start
            lexer lexer_make_token
        endwhile
    endlet
endproc

proc main
    mem lexer sizeof(Lexer) endmem

    lexer "10 10 + print\n" lexer_init
    lexer lexer_lex
    lexer lexer_free
endproc main