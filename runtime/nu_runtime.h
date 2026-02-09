#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

// VALUE

typedef enum {
    TYPE_INT,
    TYPE_FLOAT,
    TYPE_PTR,
} ValueType;

#define INT   intptr_t
#define FLOAT double
#define PTR   void*

typedef struct {
    ValueType type;
    union {
        INT   ival;
        FLOAT fval;
        PTR   pval;
    } as;
} Value;

#define VAL_INT(x)   (Value){.type = TYPE_INT,   .as.ival = (INT)(x)}
#define VAL_FLOAT(x) (Value){.type = TYPE_FLOAT, .as.fval = (FLOAT)(x)}
#define VAL_PTR(x)   (Value){.type = TYPE_PTR,   .as.pval = (PTR)(x)}

#define IS_INT(x)   (x).type == TYPE_INT
#define IS_FLOAT(x) (x).type == TYPE_FLOAT
#define IS_PTR(x)   (x).type == TYPE_PTR

#define AS_INT(x)   (x).as.ival
#define AS_FLOAT(x) (x).as.fval
#define AS_PTR(x)   (x).as.pval

void value_print(Value val);
bool value_as_bool(Value val);

Value value_add(Value a, Value b);
Value value_sub(Value a, Value b);
Value value_mul(Value a, Value b);
Value value_div(Value a, Value b);

Value value_equal(Value a, Value b);
Value value_greater(Value a, Value b);
Value value_less(Value a, Value b);

Value value_to_int(Value val);
Value value_to_float(Value val);
Value value_to_ptr(Value val);

// STACK

typedef struct {
    Value* data;
    size_t capacity;
    size_t size;
} ValueStack;

void  stack_init(ValueStack *s);
void  stack_free(ValueStack *s);
void  stack_push(ValueStack *s, Value val);
Value stack_pop(ValueStack *s);

Value stack_pick(ValueStack *s, size_t index);
void  stack_roll(ValueStack *s, size_t index);