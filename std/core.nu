macro $char $int endmacro
macro $bool $int endmacro

macro true  1 $bool endmacro
macro false 0 $bool endmacro

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

macro @ptr @64 $ptr endmacro
macro !ptr !64      endmacro

macro sizeof(char) 1 endmacro
macro sizeof(int)  8 endmacro
macro sizeof(ptr)  8 endmacro