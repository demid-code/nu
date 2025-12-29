#pragma once

#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>

// VALUE

typedef enum {
    TYPE_INT,
    TYPE_FLOAT,
    TYPE_BOOL,
    TYPE_PTR,
} ValueType;

typedef struct {
    ValueType type;
    union {
        int intVal;
        double floatVal;
        bool boolVal;
        void* ptrVal;
    } as;
} Value;

#define VAL_INT(v)   ((Value){.type = TYPE_INT, .as.intVal = (int)(v)})
#define VAL_FLOAT(v) ((Value){.type = TYPE_FLOAT, .as.floatVal = (double)(v)})
#define VAL_BOOL(v)  ((Value){.type = TYPE_BOOL, .as.boolVal = (bool)(v)})
#define VAL_PTR(v)   ((Value){.type = TYPE_PTR, .as.ptrVal = (void*)(v)})

#define AS_INT(v)   (v.as.intVal)
#define AS_FLOAT(v) (v.as.floatVal)
#define AS_BOOL(v)  (v.as.boolVal)
#define AS_PTR(v)   (v.as.ptrVal)

#define IS_INT(v)   (v.type == TYPE_INT)
#define IS_FLOAT(v) (v.type == TYPE_FLOAT)
#define IS_BOOL(v)  (v.type == TYPE_BOOL)
#define IS_PTR(v)   (v.type == TYPE_PTR)

void value_print(Value val);

Value value_add(Value a, Value b);

// STACK

typedef struct {
    Value* data;
    size_t size;
    size_t capacity;
} ValueStack;

void  stack_init(ValueStack* s);
void  stack_free(ValueStack* s);
void  stack_push(ValueStack* s, Value val);
Value stack_pop(ValueStack* s);