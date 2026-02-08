include "std/core.nu"

macro N 10 endmacro

1 while dup N 1 + < do
    dup print
    1 +
endwhile drop