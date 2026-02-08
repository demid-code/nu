include "std/core.nu"

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

macro fputs // filepath buf
    sizeof(char) over cstrlen 3 roll fwrite drop
endmacro

macro puts  stdout swap fputs endmacro // buf
macro eputs stderr swap fputs endmacro // buf