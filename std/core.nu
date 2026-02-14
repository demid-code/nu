macro $char $int endmacro
macro $bool $int endmacro

macro true  1 endmacro
macro false 0 endmacro

macro != == not endmacro
macro <= >  not endmacro
macro >= <  not endmacro

macro dup  0 pick endmacro
macro over 1 pick endmacro
macro swap 1 roll endmacro
macro rot  2 roll endmacro

macro @char @8 endmacro
macro !char !8 endmacro

macro @int @64 endmacro
macro !int !64 endmacro

macro @bool @64 endmacro
macro !bool !64 endmacro

macro @ptr @64 $ptr endmacro
macro !ptr !64      endmacro

const sizeof(char) 1 endconst
const sizeof(int)  8 endconst
const sizeof(bool) 8 endconst
const sizeof(ptr)  8 endconst