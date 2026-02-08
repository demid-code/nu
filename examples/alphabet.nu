include "std/std.nu"

macro N 26 endmacro

// lower
0 while dup N < do
    dup 'a' + putc
    1 +
endwhile drop '\n' putc

// upper
0 while dup N < do
    dup 'A' + putc
    1 +
endwhile drop '\n' putc