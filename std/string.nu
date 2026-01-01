proc cstrlen in // ptr -> int
    let ptr in
        0 while true do
            ptr over sizeof(char) * + @char '\0' == if
                break
            endif

            1 +
        endwhile
    endlet
endproc

proc cstreq in // ptr ptr -> bool
    let str1 str2 in
        str1 cstrlen str2 cstrlen == if
            str1 cstrlen 0 while dup 2 pick < do
                str1 over   sizeof(char) * + @8
                str2 2 pick sizeof(char) * + @8

                != if break endif

                1 +
            endwhile

            swap < not
        else
            false
        endif
    endlet
endproc