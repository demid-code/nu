include "std/core.nu"
include "std/string.nu"
include "std/std.nu"

cmacro stdin  stack_push(&stack, VAL_PTR(stdin));  endcmacro
cmacro stdout stack_push(&stack, VAL_PTR(stdout)); endcmacro
cmacro stderr stack_push(&stack, VAL_PTR(stderr)); endcmacro

cmacro fwrite // buf elementSize bufSize fp -> bytesWritten
    Value fp = stack_pop(&stack);
    Value bufSize = stack_pop(&stack);
    Value elemSize = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    size_t ret = fwrite(AS_PTR(buf), (size_t)AS_INT(elemSize), (size_t)AS_INT(bufSize), (FILE*)AS_PTR(fp));
    stack_push(&stack, VAL_INT(ret));
endcmacro

macro puts // ptr -> ...
    sizeof(char) over cstrlen stdout fwrite
endmacro

macro eputs // ptr -> ...
    sizeof(char) over cstrlen stderr fwrite
endmacro

proc putc in // int -> ../
    sizeof(char) malloc

    bind char ptr endbind
        char ptr !8
        ptr sizeof(char) 1 stdout fwrite
    unbind*
endproc

proc eputc in // int -> ../
    sizeof(char) malloc

    bind char ptr endbind
        char ptr !8
        ptr sizeof(char) 1 stderr fwrite
    unbind*
endproc