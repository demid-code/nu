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
        case TYPE_BOOL:  ERROR("Can't add booleans");
        case TYPE_PTR:   ERROR("Can't add pointers");
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b))      return VAL_FLOAT((double)AS_INT(a) + AS_FLOAT(b));
        else if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) + (double)AS_INT(b));
        else if (IS_PTR(a) && IS_INT(b))   return VAL_PTR(AS_PTR(a) + AS_INT(b));
        else if (IS_INT(a) && IS_PTR(b))   return VAL_PTR(AS_PTR(b) + AS_INT(a));
        ERROR("Invalid types in value_add");
    }
}

Value value_sub(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) - AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) - AS_FLOAT(b));
        case TYPE_BOOL:  ERROR("Can't subtract booleans");
        case TYPE_PTR:   ERROR("Can't subtract pointers");
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b))      return VAL_FLOAT((double)AS_INT(a) - AS_FLOAT(b));
        else if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) - (double)AS_INT(b));
        else if (IS_PTR(a) && IS_INT(b))   return VAL_PTR(AS_PTR(a) - AS_INT(b));
        else if (IS_INT(a) && IS_PTR(b))   return VAL_PTR(AS_PTR(b) - AS_INT(a));
        ERROR("Invalid types in value_sub");
    }
}

Value value_mul(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_INT(AS_INT(a) * AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) * AS_FLOAT(b));
        case TYPE_BOOL:  ERROR("Can't multiply booleans");
        case TYPE_PTR:   ERROR("Can't multiply pointers");
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b))      return VAL_FLOAT((double)AS_INT(a) * AS_FLOAT(b));
        else if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) * (double)AS_INT(b));
        ERROR("Invalid types in value_mul");
    }
}

Value value_div(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_FLOAT(AS_INT(a) / AS_INT(b));
        case TYPE_FLOAT: return VAL_FLOAT(AS_FLOAT(a) / AS_FLOAT(b));
        case TYPE_BOOL:  ERROR("Can't divide booleans");
        case TYPE_PTR:   ERROR("Can't divide pointers");
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b))      return VAL_FLOAT((double)AS_INT(a) / AS_FLOAT(b));
        else if (IS_FLOAT(a) && IS_INT(b)) return VAL_FLOAT(AS_FLOAT(a) / (double)AS_INT(b));
        ERROR("Invalid types in value_div");
    }
}

Value value_equal(Value a, Value b) {
    if (a.type != b.type) return VAL_BOOL(false);

    switch (a.type) {
    case TYPE_INT:   return VAL_BOOL(AS_INT(a) == AS_INT(b));
    case TYPE_FLOAT: return VAL_BOOL(AS_FLOAT(a) == AS_FLOAT(b));
    case TYPE_BOOL:  return VAL_BOOL(AS_BOOL(a) == AS_BOOL(b));
    case TYPE_PTR:   return VAL_BOOL(AS_PTR(a) == AS_PTR(b));
    }
}

Value value_greater(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_BOOL(AS_INT(a) > AS_INT(b));
        case TYPE_FLOAT: return VAL_BOOL(AS_FLOAT(a) > AS_FLOAT(b));
        case TYPE_BOOL:  ERROR("Can't compare if boolean is greater");
        case TYPE_PTR:   ERROR("Can't compare if pointer is greater");
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b))      return VAL_BOOL((double)AS_INT(a) > AS_FLOAT(b));
        else if (IS_FLOAT(a) && IS_INT(b)) return VAL_BOOL(AS_FLOAT(a) > (double)AS_INT(b));
        ERROR("Invalid types in value_greater");
    }
}

Value value_less(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
        case TYPE_INT:   return VAL_BOOL(AS_INT(a) < AS_INT(b));
        case TYPE_FLOAT: return VAL_BOOL(AS_FLOAT(a) < AS_FLOAT(b));
        case TYPE_BOOL:  ERROR("Can't compare if boolean is less");
        case TYPE_PTR:   ERROR("Can't compare if pointer is less");
        }
    } else {
        if (IS_INT(a) && IS_FLOAT(b))      return VAL_BOOL((double)AS_INT(a) < AS_FLOAT(b));
        else if (IS_FLOAT(a) && IS_INT(b)) return VAL_BOOL(AS_FLOAT(a) < (double)AS_INT(b));
        ERROR("Invalid types in value_less");
    }
}

Value value_to_int(Value val) {
    switch (val.type) {
    case TYPE_INT:   return val;
    case TYPE_FLOAT: return VAL_INT(AS_FLOAT(val));
    case TYPE_BOOL:  return VAL_INT(AS_BOOL(val));
    case TYPE_PTR:   ERROR("Can't convert ptr to int");
    }
}

Value value_to_float(Value val) {
    switch (val.type) {
    case TYPE_INT:   return VAL_FLOAT(AS_INT(val));
    case TYPE_FLOAT: return val;
    case TYPE_BOOL:  return VAL_FLOAT(AS_BOOL(val));
    case TYPE_PTR:   ERROR("Can't convert ptr to float");
    }
}

Value value_to_bool(Value val) {
    switch (val.type) {
    case TYPE_INT:   return VAL_BOOL(AS_INT(val));
    case TYPE_FLOAT: return VAL_BOOL(AS_FLOAT(val));
    case TYPE_BOOL:  return val;
    case TYPE_PTR:   ERROR("Can't convert ptr to bool");
    }
}

// STACK

void stack_init(ValueStack *s) {
    s->size = 0;
    s->capacity = 8;
    s->data = (Value*)malloc(s->capacity * sizeof(Value));
    if (!s->data) ERROR("Failed to allocate memory in stack_init");
}

void stack_free(ValueStack *s) {
    free(s->data);
    s->data = NULL;
    s->size = 0;
    s->capacity = 0;
}

void stack_push(ValueStack *s, Value val) {
    if (s->size >= s->capacity) {
        s->capacity *= 2;
        s->data = (Value*)realloc(s->data, s->capacity * sizeof(Value));
        if (!s->data) ERROR("Failed to reallocate memory in stack_push");
    }

    s->data[s->size++] = val;
}

Value stack_pop(ValueStack *s) {
    if (s->size <= 0) ERROR("Stack underflow");

    return s->data[--s->size];
}

// check for index
void stack_pick(ValueStack *s, size_t index) {
    if (index < 0 || index >= s->size) ERROR("Invalid index in stack_pick");

    stack_push(s, s->data[s->size - index - 1]);
}

void stack_roll(ValueStack *s, size_t index) {
    if (index < 0 || index >= s->size) ERROR("Invalid index in stack_roll");

    Value value = s->data[s->size - index - 1];

    for (size_t i = s->size - index - 1; i < s->size - 1; i++) {
        s->data[i] = s->data[i+1];
    }

    s->data[s->size - 1] = value;
}