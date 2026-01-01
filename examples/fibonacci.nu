include "std/core.nu"

macro N 16 endmacro

0 1 over over swap print print

0 while dup N 2 - < do
    rot 2 pick +
    dup print
    swap

    1 +
endwhile

drop drop drop