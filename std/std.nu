cmacro malloc // int -> ptr
    Value size = stack_pop(&stack);
    void* buf = malloc((size_t)AS_INT(size));
    stack_push(&stack, VAL_PTR(buf));
endcmacro

// TODO: write realloc, maybe you can make it without cmacro?

cmacro free // ptr -> ...
    Value ptr = stack_pop(&stack);
    free(AS_PTR(ptr));
endcmacro