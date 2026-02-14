include "std/core.nu"

proc abs // int -> int
    dup 0 < if
        -1 *
    endif
endproc