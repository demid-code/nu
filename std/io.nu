include "std/core.nu"
include "std/string.nu"
include "std/std.nu"

cmacro stdin  stack_push(&stack, VAL_PTR(stdin));  endcmacro
cmacro stdout stack_push(&stack, VAL_PTR(stdout)); endcmacro
cmacro stderr stack_push(&stack, VAL_PTR(stderr)); endcmacro

// buf elementSize bufSize fp -> bytesWritten
cmacro fwrite
    Value fp = stack_pop(&stack);
    Value bufSize = stack_pop(&stack);
    Value elemSize = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    size_t ret = fwrite(AS_PTR(buf), (size_t)AS_INT(elemSize), (size_t)AS_INT(bufSize), (FILE*)AS_PTR(fp));
    stack_push(&stack, VAL_INT(ret));
endcmacro

macro puts // ptr -> ...
    sizeof(char) over cstrlen stdout fwrite drop
endmacro

macro eputs // ptr -> ...
    sizeof(char) over cstrlen stderr fwrite drop
endmacro

proc putc in // int -> ../
    sizeof(char) malloc

    bind char ptr endbind
        char ptr !8
        ptr sizeof(char) 1 stdout fwrite drop
    unbind*
endproc

proc eputc in // int -> ../
    sizeof(char) malloc

    bind char ptr endbind
        char ptr !8
        ptr sizeof(char) 1 stderr fwrite drop
    unbind*
endproc

proc putb in // bool -> ...
    if   "true"  puts
    else "false" puts endif
endproc

proc eputb in // bool -> ...
    if   "true"  eputs
    else "false" eputs endif
endproc