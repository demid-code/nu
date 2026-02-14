#include "nu_runtime.h"

// VALUE

void value_print(Value val) {
    switch (val.type) {
    case TYPE_INT:   printf("%d\n", AS_INT(val));    break;
    case TYPE_FLOAT: printf("%g\n", AS_FLOAT(val));  break;
    case TYPE_PTR:   printf("%p\n", AS_PTR(val));    break;
    }
}

bool value_as_bool(Value val) {
    switch (val.type) {
    case TYPE_INT:   return AS_INT(val) > 0;
    case TYPE_FLOAT: return AS_FLOAT(val) > 0;
    case TYPE_PTR:   return AS_PTR(val) != NULL;
    }
}

Value value_add(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) + AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) + AS_FLOAT(b));
        case TYPE_PTR: fprintf(stderr, "Error: Can't add up pointers"); exit(1);
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_FLOAT((FLOAT)AS_INT(a) + AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) + (FLOAT)AS_INT(b));
        if (IS_INT(a) && IS_PTR(b))   return VAL_PTR(AS_PTR(b) + AS_INT(a));
        if (IS_PTR(a) && IS_INT(b))   return VAL_PTR(AS_PTR(a) + AS_INT(b));
        fprintf(stderr, "Error: Invalid types in value_add\n");
        exit(1);
    }
}

Value value_sub(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) - AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) - AS_FLOAT(b));
        case TYPE_PTR:   return VAL_PTR(AS_PTR(a) - AS_PTR(b));
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_FLOAT((FLOAT)AS_INT(a) - AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) - (FLOAT)AS_INT(b));
        if (IS_INT(a) && IS_PTR(b))   return VAL_PTR(AS_PTR(b) - AS_INT(a));
        if (IS_PTR(a) && IS_INT(b))   return VAL_PTR(AS_PTR(a) - AS_INT(b));
        fprintf(stderr, "Error: Invalid types in value_sub\n");
        exit(1);
    }
}

Value value_mul(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) * AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) * AS_FLOAT(b));
        case TYPE_PTR: fprintf(stderr, "Error: Can't multiply pointers"); exit(1);
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_FLOAT((FLOAT)AS_INT(a) * AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) * (FLOAT)AS_INT(b));
        fprintf(stderr, "Error: Invalid types in value_mul\n");
        exit(1);
    }
}

Value value_div(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_FLOAT((FLOAT)AS_INT(a) / (FLOAT)AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) + AS_FLOAT(b));
        case TYPE_PTR: fprintf(stderr, "Error: Can't divide pointers"); exit(1);
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_FLOAT((FLOAT)AS_INT(a) / AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) / (FLOAT)AS_INT(b));
        fprintf(stderr, "Error: Invalid types in value_div\n");
        exit(1);
    }
}

Value value_mod(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) % AS_INT(b));
        case TYPE_FLOAT: fprintf(stderr, "Error: Can't apply modulo to floats"); exit(1);
        case TYPE_PTR:   fprintf(stderr, "Error: Can't apply modulo to pointers"); exit(1);
        }
    } else {
        fprintf(stderr, "Error: Invalid types in value_mod\n");
        exit(1);
    }
}

Value value_equal(Value a, Value b) {
    if (a.type != b.type) return VAL_INT(0);

    switch (a.type) {
    case TYPE_INT:   return VAL_INT(AS_INT(a) == AS_INT(b));
    case TYPE_FLOAT: return VAL_INT(AS_FLOAT(a) == AS_FLOAT(b));
    case TYPE_PTR:   return VAL_INT(AS_PTR(a) == AS_PTR(b));
    }
}

Value value_greater(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a)   > AS_INT(b));
        case TYPE_FLOAT: return VAL_INT(AS_FLOAT(a) > AS_FLOAT(b));
        case TYPE_PTR:   return VAL_INT(AS_PTR(a)   > AS_PTR(b));
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_INT((FLOAT)AS_INT(a) > AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_INT(AS_FLOAT(a)      > (FLOAT)AS_INT(b));
        fprintf(stderr, "Error: Invalid types in value_greater\n");
        exit(1);
    }
}

Value value_less(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a)   < AS_INT(b));
        case TYPE_FLOAT: return VAL_INT(AS_FLOAT(a) < AS_FLOAT(b));
        case TYPE_PTR:   return VAL_INT(AS_PTR(a)   < AS_PTR(b));
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_INT((FLOAT)AS_INT(a) < AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_INT(AS_FLOAT(a)      < (FLOAT)AS_INT(b));
        fprintf(stderr, "Error: Invalid types in value_less\n");
        exit(1);
    }
}

Value value_to_int(Value val) {
    switch (val.type) {
    case TYPE_INT:   return val;
    case TYPE_FLOAT: return VAL_INT((INT)AS_FLOAT(val));
    }

    fprintf(stderr, "Error: Unreachable in value_to_int\n");
    exit(1);
}

Value value_to_float(Value val) {
    switch (val.type) {
    case TYPE_INT:   return VAL_FLOAT((FLOAT)AS_INT(val));
    case TYPE_FLOAT: return val;
    }

    fprintf(stderr, "Error: Unreachable in value_to_float\n");
    exit(1);
}

Value value_to_ptr(Value val) {
    switch (val.type) {
    case TYPE_INT: return VAL_PTR((uint64_t*)(uint64_t)AS_INT(val));
    case TYPE_PTR: return val;
    }

    fprintf(stderr, "Error: Unreachable in value_to_ptr\n");
    exit(1);
}

// STACK

void stack_init(ValueStack *s) {
    s->capacity = 8;
    s->size = 0;
    s->data = (Value*)malloc(s->capacity * sizeof(Value));
    if (!s->data) {
        fprintf(stderr, "Error: Failed to allocate memory in stack_init\n");
        exit(1);
    }
}

void stack_free(ValueStack *s) {
    free(s->data);
    s->data = NULL;
    s->capacity = 0;
    s->size = 0;
}

void stack_push(ValueStack *s, Value val) {
    if (s->size >= s->capacity) {
        s->capacity *= 2;
        s->data = (Value*)realloc(s->data, s->capacity * sizeof(Value));
        if (!s->data) {
            fprintf(stderr, "Error: Failed to reallocate memory in stack_push\n");
            exit(1);
        }
    }

    s->data[s->size++] = val;
}

Value stack_pop(ValueStack *s) {
    if (s->size == 0) {
        fprintf(stderr, "Error: Stack Underflow\n");
        exit(1);
    }

    return s->data[--s->size];
}

Value stack_pick(ValueStack *s, size_t index) {
    if (index < 0 || index > s->size - 1) {
        fprintf(stderr, "Error: Invalid index in stack_pick\n");
        exit(1);
    }

    return s->data[s->size - index - 1];
}

void stack_roll(ValueStack *s, size_t index) {
    if (index < 0 || index > s->size - 1) {
        fprintf(stderr, "Error: Invalid index in stack_pick\n");
        exit(1);
    }

    size_t pos = s->size - index - 1;
    Value val = s->data[pos];

    for (size_t i = pos; i < s->size - 1; i++) {
        s->data[i] = s->data[i + 1];
    }

    s->data[s->size - 1] = val;
}