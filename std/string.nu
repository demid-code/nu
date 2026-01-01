proc cstrlen in // ptr -> int
    0 while true do
        over over sizeof(char) * + @char '\0' == if
            break
        endif

        1 +
    endwhile
    
    swap drop
endproc

proc cstreq in // ptr ptr -> bool
    // if length of 2 ptr is different, return false
    over cstrlen over cstrlen != if
        drop drop
        false return
    endif

    // checking if each char is equals, if not return false
    dup cstrlen 0 while dup 2 pick < do
        3 pick over   sizeof(char) * + @char
        3 pick 2 pick sizeof(char) * + @char
        
        != if
            drop drop drop drop
            false return
        endif

        1 +
    endwhile

    drop drop drop drop
    true
endproc