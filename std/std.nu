include "std/core.nu"

cmacro malloc // size -> ptr
    Value size = stack_pop(&stack);
    stack_push(&stack, VAL_PTR(malloc((size_t)AS_INT(size))));
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

macro cstr_to_str // cstr
    dup cstrlen
endmacro

macro cstrlen // cstr -> int
    true 0 while over do
        1 +

        2 pick over sizeof(char) * + @char
        '\0' == if
            swap drop false swap
        endif
    endwhile

    swap drop swap drop
endmacro

macro cstreq // cstr cstr -> bool
    over cstrlen over cstrlen == if
        true over cstrlen 0
        while dup 2 pick < do
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
        drop drop false
    endif
endmacro

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

macro fputc // filepath char
    sizeof(char) malloc
    swap over !char
    dup sizeof(char) 1 4 roll fwrite drop
    free
endmacro

macro putc  stdout swap fputc endmacro // char
macro eputc stderr swap fputc endmacro // char

macro Str.data    0                      endmacro
macro Str.len     Str.data sizeof(ptr) + endmacro
macro sizeof(Str) Str.len sizeof(int)  + endmacro

macro @Str.data Str.data + @ptr endmacro
macro @Str.len  Str.len  + @int endmacro

macro !Str.data Str.data + !ptr endmacro
macro !Str.len  Str.len  + !int endmacro

macro @Str // Str -> cstr len
    dup @Str.data
    over @Str.len
    rot drop
endmacro

macro !Str // cstr len Str -> Str
    swap over !Str.len
    swap over !Str.data
endmacro