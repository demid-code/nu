macro cstrlen // ptr -> int
    0 while true do
        over over sizeof(char) * + @char '\0' == if
            break
        endif

        1 +
    endwhile
    
    swap drop
endmacro