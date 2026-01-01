macro true  1 $bool endmacro
macro false 0 $bool endmacro

macro != == not endmacro
macro >= <  not endmacro
macro <= >  not endmacro

macro dup  0 pick endmacro
macro over 1 pick endmacro
macro swap 1 roll endmacro
macro rot  2 roll endmacro

macro @char @8 endmacro

macro sizeof(char) 1 endmacro