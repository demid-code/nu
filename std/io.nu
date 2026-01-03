include "std/core.nu"
include "std/string.nu"
include "std/std.nu"
include "std/math.nu"

cmacro stdin  stack_push(&stack, VAL_PTR(stdin));  endcmacro
cmacro stdout stack_push(&stack, VAL_PTR(stdout)); endcmacro
cmacro stderr stack_push(&stack, VAL_PTR(stderr)); endcmacro

// buffer: ptr, size: int, count: int stream: ptr -> bytes: int
cmacro fwrite
    Value stream = stack_pop(&stack);
    Value count = stack_pop(&stack);
    Value size = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    size_t ret = fwrite(AS_PTR(buf), (size_t)AS_INT(size), (size_t)AS_INT(count), (FILE*)AS_PTR(stream));
    stack_push(&stack, VAL_INT(ret));
endcmacro

// buffer: ptr, size: int, count: int stream: ptr -> bytes: int
cmacro fread
    Value stream = stack_pop(&stack);
    Value count = stack_pop(&stack);
    Value size = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    int bytes = fread(AS_PTR(buf), (size_t)AS_INT(size), (size_t)AS_INT(count), (FILE*)AS_PTR(stream));
    stack_push(&stack, VAL_INT(bytes));
endcmacro

// filename: ptr, mode: ptr -> fp: ptr
cmacro fopen
    Value mode = stack_pop(&stack);
    Value filename = stack_pop(&stack);
    FILE* fp = fopen((char*)AS_PTR(filename), (char*)AS_PTR(mode));
    stack_push(&stack, VAL_PTR(fp));
endcmacro

// fp: ptr -> int
cmacro fclose
    Value fp = stack_pop(&stack);
    int ret = fclose((FILE*)AS_PTR(fp));
    stack_push(&stack, VAL_INT(ret));
endcmacro

macro fputs // ptr fp -> ...
    sizeof(char) swap 2 pick cstrlen swap fwrite drop
endmacro

macro puts  stdout fputs endmacro // ptr -> ...
macro eputs stdout fputs endmacro // ptr -> ...

proc fputc in // int fp -> ...
    sizeof(char) malloc // buffer

    bind char fp ptr endbind
        char ptr !char
        ptr sizeof(char) 1 fp fwrite drop
    unbind*
endproc

macro putc  stdout fputc endmacro // int -> ...
macro eputc stderr fputc endmacro // int -> ...

proc fputb in // bool fp -> ...
    swap if "true"  swap fputs
    else    "false" swap fputs endif
endproc

macro putb  stdout fputb endmacro // bool -> ...
macro eputb stderr fputb endmacro // bool -> ...

proc fputi in // int fp -> ...
    over 0 < rot abs
    bind fp isNegative num endbind

    // calculating buffer size
    num 0 while true do
        swap 10 / $int swap
        over 0 == if
            swap drop 1 + break
        endif
        
        1 +
    endwhile
    isNegative if 1 + endif

    dup sizeof(char) * malloc // allocating buffer
    
    bind len buf endbind
        // writing to buffer
        isNegative if '-' buf !char endif
    
        num 0 while dup len < do
            dup len 1 - == isNegative and if
                break
            endif

            swap dup 10 % '0' +                         // getting digit char
            buf len 4 pick - 1 - sizeof(char) * + !char // writing char
            10 / $int swap                              // dividing initial number
            
            1 +
        endwhile

        // outputing buffer
        buf sizeof(char) len fp fwrite drop
    unbind*
endproc

macro puti  stdout fputi endmacro // int -> ...
macro eputi stderr fputi endmacro // int -> ...