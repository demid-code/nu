macro EXIT_SUCCESS 0 endmacro
macro EXIT_FAILURE 1 endmacro

cmacro exit // int -> ...
    Value code = stack_pop(&stack);
    exit(AS_INT(code));
endcmacro