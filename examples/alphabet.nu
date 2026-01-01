include "std/io.nu"

macro N 26 endmacro

// lowercase

0 while dup N < do
    dup 'a' + putc
    1 +
endwhile drop
'\n' putc

// uppercase

0 while dup N < do
    dup 'A' + putc
    1 +
endwhile drop
'\n' putc