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

macro cstreq // str str -> bool
    over cstrlen over cstrlen == if
        true over cstrlen 0
        while dup 2 pick < do
            4 pick over   sizeof(char) * + @char // 1 char
            4 pick 2 pick sizeof(char) * + @char // 2 char

            != if
                drop drop drop
                false 2 2
            endif

            1 +
        endwhile
        drop drop swap drop swap drop
    else
        drop drop false
    endif
endmacro

macro fputs // filepath buf
    sizeof(char) over cstrlen 3 roll fwrite drop
endmacro

macro puts  stdout swap fputs endmacro // buf
macro eputs stderr swap fputs endmacro // buf

macro fputc // filepath char
    sizeof(char) malloc
    swap over !char
    dup sizeof(char) 1 4 roll fwrite drop
    free
endmacro

macro putc  stdout swap fputc endmacro // char
macro eputc stderr swap fputc endmacro // char