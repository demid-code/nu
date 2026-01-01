macro EXIT_SUCCESS 0 endmacro
macro EXIT_FAILURE 1 endmacro

cmacro exit // int -> ...
    Value code = stack_pop(&stack);
    exit(AS_INT(code));
endcmacro

cmacro malloc // int -> ptr
    Value size = stack_pop(&stack);
    void* buf = malloc((size_t)AS_INT(size));
    stack_push(&stack, VAL_PTR(buf));
endcmacro

cmacro free // ptr -> ...
    Value ptr = stack_pop(&stack);
    free(AS_PTR(ptr));
endcmacro