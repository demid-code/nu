cmacro stdin  stack_push(&stack, VAL_PTR(stdin));  endcmacro
cmacro stdout stack_push(&stack, VAL_PTR(stdout)); endcmacro
cmacro stderr stack_push(&stack, VAL_PTR(stderr)); endcmacro

cmacro fwrite // buf elementSize bufSize fp -> bytesWritten
    Value fp = stack_pop(&stack);
    Value bufSize = stack_pop(&stack);
    Value elemSize = stack_pop(&stack);
    Value buf = stack_pop(&stack);
    size_t ret = fwrite(AS_PTR(buf), (size_t)AS_INT(elemSize), (size_t)AS_INT(bufSize), (FILE*)AS_PTR(fp));
    stack_push(&stack, VAL_INT(ret));
endcmacro