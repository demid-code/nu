#include "nu_runtime.h"

// VALUE

void value_print(Value val) {
    switch (val.type) {
    case TYPE_INT:   printf("%d\n", AS_INT(val)); break;
    case TYPE_FLOAT: printf("%g\n", AS_FLOAT(val)); break;
    case TYPE_BOOL:
        if (AS_BOOL(val)) { printf("true\n"); }
        else { printf("false\n"); }
        break;
    case TYPE_PTR: printf("%p\n", AS_PTR(val)); break;
    }
}

Value value_add(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) + AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) + AS_FLOAT(b));
        case TYPE_BOOL:  {
            fprintf(stderr, "Can't add booleans\n");
            exit(1);
        }
        case TYPE_PTR: {
            fprintf(stderr, "Can't add pointers\n");
            exit(1);
        }
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b)) return VAL_FLOAT((double)AS_INT(a) + AS_FLOAT(b));
        if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) + (double)AS_INT(b));
        if (IS_PTR(a) && IS_INT(b)) {
            return VAL_PTR(a.as.ptrVal + AS_INT(b));
        }
    }
}

// STACK

void stack_init(ValueStack* s) {
    s->size = 0;
    s->capacity = 8;
    s->data = (Value*)malloc(s->capacity * sizeof(Value));
    if (!s->data) {
        fprintf(stderr, "Failed to allocate memory in stack_init\n");
        exit(1);
    }
}

void stack_free(ValueStack* s) {
    free(s->data);
    s->data = NULL;
    s->size = 0;
    s->capacity = 0;
}

void stack_push(ValueStack* s, Value val) {
    if (s->size >= s->capacity) {
        s->capacity *= 2;
        s->data = (Value*)realloc(s->data, s->capacity * sizeof(Value));
        if (!s->data) {
            fprintf(stderr, "Failed to reallocate memory in stack_push\n");
            exit(1);
        }
    }

    s->data[s->size++] = val;
}

Value stack_pop(ValueStack* s) {
    if (s->size <= 0) {
        fprintf(stderr, "Stack underflow\n");
        exit(1);
    }

    return s->data[--s->size];
}