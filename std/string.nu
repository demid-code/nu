include "std/core.nu"

const Str.data    reset              endconst
const Str.len     sizeof(ptr) offset endconst
const sizeof(Str) sizeof(int) offset endconst

macro @Str.data Str.data + @ptr endmacro
macro @Str.len  Str.len  + @int endmacro

macro !Str.data Str.data + !ptr endmacro
macro !Str.len  Str.len  + !int endmacro

proc @Str // Str -> cstr len
    let str in
        str @Str.data
        str @Str.len
    endlet
endproc

proc !Str // cstr len Str
    let cstr len Str in
        cstr Str !Str.data
        len  Str !Str.len
    endlet
endproc