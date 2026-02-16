include "std/core.nu"
include "std/math.nu"

cmacro NULL stack_push(&stack, VAL_PTR(NULL)); endcmacro // ... -> ptr

cmacro exit
    Value code = stack_pop(&stack);
    exit((int)AS_INT(code));
endcmacro

cmacro malloc // size -> ptr
    Value size = stack_pop(&stack);
    stack_push(&stack, VAL_PTR(malloc((size_t)AS_INT(size))));
endcmacro

cmacro realloc // size ptr -> ptr
    Value ptr = stack_pop(&stack);
    Value size = stack_pop(&stack);
    void *newPtr = realloc((void*)AS_PTR(ptr), (size_t)AS_INT(size));
    stack_push(&stack, VAL_PTR(newPtr));
endcmacro

cmacro free // ptr
    Value ptr = stack_pop(&stack);
    free((void*)AS_PTR(ptr));
endcmacro

cmacro stdin  stack_push(&stack, VAL_PTR(stdin));  endcmacro
cmacro stdout stack_push(&stack, VAL_PTR(stdout)); endcmacro
cmacro stderr stack_push(&stack, VAL_PTR(stderr)); endcmacro

cmacro fwrite // buf size count stream -> bytesWritten
    Value stream = stack_pop(&stack);
    Value count = stack_pop(&stack);
    Value size = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    size_t bw = fwrite((void*)AS_PTR(buf), (size_t)AS_INT(size), (size_t)AS_INT(count), (FILE*)AS_PTR(stream));
    stack_push(&stack, VAL_INT(bw));
endcmacro

cmacro fopen // path pathlen mode modelen -> file
    stack_pop(&stack);
    Value mode = stack_pop(&stack);
    stack_pop(&stack);
    Value path = stack_pop(&stack);
    FILE *f = fopen((char*)AS_PTR(path), (char*)AS_PTR(mode));
    stack_push(&stack, VAL_PTR(f));
endcmacro

cmacro fclose // file -> int
    Value file = stack_pop(&stack);
    stack_push(&stack, VAL_INT(fclose((FILE*)AS_PTR(file))));
endcmacro

cmacro SEEK_SET stack_push(&stack, VAL_INT(SEEK_SET)); endcmacro // ... -> int
cmacro SEEK_CUR stack_push(&stack, VAL_INT(SEEK_CUR)); endcmacro // ... -> int
cmacro SEEK_END stack_push(&stack, VAL_INT(SEEK_END)); endcmacro // ... -> int

cmacro fseek // file offset origin -> int
    Value origin = stack_pop(&stack);
    Value offset = stack_pop(&stack);
    Value file = stack_pop(&stack);
    stack_push(&stack, VAL_INT(fseek((FILE*)AS_PTR(file), (long)AS_INT(offset), (int)AS_INT(origin))));
endcmacro

cmacro ftell // file -> int
    Value file = stack_pop(&stack);
    stack_push(&stack, VAL_INT(ftell((FILE*)AS_PTR(file))));
endcmacro

cmacro fread // buf size count file -> int
    Value file = stack_pop(&stack);
    Value count = stack_pop(&stack);
    Value size = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    stack_push(&stack, VAL_INT(fread((void*)AS_PTR(buf), (size_t)AS_INT(size), (size_t)AS_INT(count), (FILE*)AS_PTR(file))));
endcmacro

// WARNING: allocates dynamic string, free it later with free
proc read_file // filepath filepathlen -> str strlen
    mem buf      sizeof(ptr) endmem
    mem filesize sizeof(int) endmem

    "rb" fopen
    
    dup NULL == if
        "Error: Can't open file\n" eputs
        -1 exit
    endif

    let file in
        file 0 SEEK_END fseek drop
        file ftell
        file 0 SEEK_SET fseek drop

        dup filesize !int
        malloc buf !ptr

        buf @ptr sizeof(char) filesize @int file fread drop

        buf @ptr filesize @int
        file fclose drop
    endlet
endproc

macro cstr_to_str // cstr
    dup cstrlen
endmacro

proc cstrlen // cstr -> int
    mem cond sizeof(bool) endmem
    true cond !bool

    let cstr in
        -1 while cond @bool do
            1 +
            cstr over + @char

            '\0' == if
                false cond !bool
            endif
        endwhile
    endlet
endproc

proc cstreq // cstr1 cstr2 -> bool
    let cstr1 cstr2 in
        cstr1 cstrlen cstr2 cstrlen == if
            mem len sizeof(int)  endmem
            mem ret sizeof(bool) endmem
            
            cstr1 cstrlen len !int
            true ret !bool

            0 while dup len @int < do
                cstr1 over + @char
                cstr2 2 pick + @char

                != if
                    drop len @int
                    false ret !bool
                endif

                1 +
            endwhile drop

            ret @bool
        else false endif
    endlet
endproc

macro streq // str1 len1 str2 len2
    2 pick over == if
        drop swap true swap 0 while dup 2 pick < do
            4 pick over   sizeof(char) * + @char // 1 char
            4 pick 2 pick sizeof(char) * + @char // 2 char

            != if
                drop drop drop
                false 1 1
            endif

            1 +
        endwhile

        drop drop swap drop swap drop
    else
        drop drop drop drop false
    endif
endmacro

macro fputs // filepath str len
    sizeof(char) swap 3 roll fwrite drop
endmacro

macro puts  stdout rot rot fputs endmacro // str len
macro eputs stderr rot rot fputs endmacro // str len

proc fputc // filepath char
    mem buf sizeof(char) endmem
    buf !char
    buf sizeof(char) 1 3 roll fwrite drop
endproc

macro putc  stdout swap fputc endmacro // char
macro eputc stderr swap fputc endmacro // char

proc fputd // filepath int
    mem numsize sizeof(int) endmem

    let fp num in
        0 num abs while dup 0 > do
            10 / $int
            swap 1 + swap
        endwhile drop numsize !int

        numsize @int
        num 0 < if 1 + endif
        dup malloc

        let bufLen buf in
            num 0 < if
                '-' buf !char
            endif

            num abs 0 while dup numsize @int < do
                swap dup 10 % '0' + buf bufLen 4 pick - 1 - + !char
                10 / $int swap

                1 +
            endwhile drop drop

            buf sizeof(char) bufLen fp fwrite drop
            buf free
        endlet
    endlet
endproc

macro putd  stdout swap fputd endmacro // int
macro eputd stderr swap fputd endmacro // int

// Char

proc is_whitespace // char -> bool
    let char in
        char ' '  ==
        char '\n' ==
        char '\r' ==
        char '\t' ==
        or or or
    endlet
endproc

proc is_digit // char -> bool
    let char in
        char '0' >=
        char '9' <=
        and
    endlet
endproc