macro EXIT_SUCCESS 0 endmacro
macro EXIT_FAILURE 1 endmacro

cmacro exit // int -> ...
    Value code = stack_pop(&stack);
    exit(AS_INT(code));
endcmacro

cmacro argc // ... -> int
    stack_push(&stack, VAL_INT(argc));
endcmacro

cmacro argv // int -> ptr
    Value index = stack_pop(&stack);
    stack_push(&stack, VAL_PTR(argv[AS_INT(index)]));
endcmacro