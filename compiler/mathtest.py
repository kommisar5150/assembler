#!/usr/bin/env python

'''
Infix calculator
First tokenize infix expression,
then transform it into postfix,
then calculate it.
E.g.:
9 - 5 + 2 * 3
=> 9 5 - 2 3 * +
'''
import re

LEFT_PAREN = '('
RIGHT_PAREN = ')'
OP_PLUS = '+'
OP_MINUS = '-'
OP_MULT = '*'
OP_DIV = '/'
OP_ATTR = {
    OP_PLUS: {'prcd': 1, 'fn': lambda a, b: a + b},
    OP_MINUS: {'prcd': 1, 'fn': lambda a, b: a - b},
    OP_MULT: {'prcd': 2, 'fn': lambda a, b: a * b},
    OP_DIV: {'prcd': 2,'fn': lambda a, b: a / b},
}
INSTRUCTIONS = {OP_PLUS: "ADD",
                OP_MINUS: "SUB",
                OP_MULT: "MUL",
                OP_DIV: "DIV"}

sep_re = re.compile(r'\s*(%s|%s|%s|%s|%s|%s)\s*' % (
                    re.escape(LEFT_PAREN),
                    re.escape(RIGHT_PAREN),
                    re.escape(OP_PLUS),
                    re.escape(OP_MINUS),
                    re.escape(OP_MULT),
                    re.escape(OP_DIV)))

def tokenize(expr):
    return [t.strip() for t in sep_re.split(expr.strip()) if t]


def in2postfix(tokens):
    opstack = []
    postfix = []
    for t in tokens:
        if t in OP_ATTR:
            while len(opstack)>0 and opstack[-1] in OP_ATTR\
                  and OP_ATTR[t]['prcd'] <= OP_ATTR[opstack[-1]]['prcd']:
                postfix.append(opstack.pop())
            opstack.append(t)
        elif t == LEFT_PAREN:
            opstack.append(t)
        elif t == RIGHT_PAREN:
            while opstack[-1] != LEFT_PAREN:
                postfix.append(opstack.pop())
            opstack.pop()
        else:
            postfix.append(t)
    postfix.extend(reversed(opstack))
    return postfix


def calc_postfix(tokens, vardict, varloc, methodvars):
    result, case, stack = 0, 0, []
    for tok in tokens:
        if tok in OP_ATTR:
            operator = INSTRUCTIONS[tok]
            op1, op2, result = stack.pop(), stack.pop(), 0
            if op1 in vardict:
                print("MEMR [4] " + str(varloc[op1]) + " $A")
                op1float = float(vardict[op1])
                case = 1

            if op2 in vardict:
                if case == 1:
                    print("MEMR [4] " + str(varloc[op2]) + " $B")
                    case = 2
                else:
                    print("MEMR [4] " + str(varloc[op2]) + " $A")
                    case = 3
                op2float = float(vardict[op2])

            if op1 in methodvars:
                offset = 4 * (methodvars.index(op1) + 1)
                print("MOV $C $S2")
                print("ADD #" + str(offset) + " $C")
                print("MEMR [4] $C $A")
                op1float = float(vardict[op1])
                case = 1

            if op2 in methodvars:
                if case == 1:
                    print("MEMR [4] " + str(varloc[op2]) + " $B")
                    case = 2
                else:
                    print("MEMR [4] " + str(varloc[op2]) + " $A")
                    case = 3
                op2float = float(vardict[op2])

            if case == 0:
                op1 = float(op1)
                op2 = float(op2)

            if case == 1:
                print(operator + " #" + str(int(op2)) + " $A")
                result = OP_ATTR[tok]['fn'](float(op2), op1float)
                stack.append(result)
                print("ADD $A $D")

            elif case == 2:
                print(operator + " $B $A")
                result = OP_ATTR[tok]['fn'](op2float, op1float)
                stack.append(result)
                print("ADD $A $D")

            elif case == 3:
                print(operator + " #" + str(int(op1)) + " $A")
                result = OP_ATTR[tok]['fn'](op2float, float(op1))
                stack.append(result)
                print("ADD $A $D")

            else:
                try:
                    stack.append(OP_ATTR[tok]['fn'](op2, op1))
                except ZeroDivisionError:
                    raise ValueError('%s %s %s ?!' % (op2, tok, op1))
        else:
            stack.append(tok)

        case = 0

    if len(stack) != 1:
        raise ValueError("invalid expression, operators and operands don't match")
    return stack.pop()

