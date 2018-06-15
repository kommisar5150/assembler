#!/usr/bin/env python

from constants import ACCEPTED_TYPES, \
                      OPERATORS

from mathtest import calc_postfix, \
                     in2postfix, \
                     tokenize

class test:

    state = 0
    varTypes = {}
    varValues = {}
    varLocation = {}
    vars = []
    functionPrototypes = []
    operandCount = 0
    memloc = 0x40000000
    methodList = []
    methodVars = []
    currentType = ""
    currentVar = ""
    currentMethod = ""
    stackOffset = 0
    mathFunction = ""


    def parseText(self, text):

        file = open(text, mode="r")
        line = file.readlines()
        output = open("output.txt", mode="w")
        for x in line:
            self.readLine(x, output)

    def readLine(self, line, output):

        line = line.split()
        if len(line) == 0:
            pass
        for x in line:

            if self.state < 7:
                self.parseMethod(x, output)
            else:
                self.parseContent(x, output)

    def parseMethod(self, x, output):

        if self.state == 0:
            if x in ACCEPTED_TYPES:
                self.currentType = x
                self.state = 1

        elif self.state == 1:
            if x not in self.methodList:
                self.methodList.append(x)
                self.state = 2
                self.currentMethod = x
            elif x in self.functionPrototypes:
                self.state = 6
                self.currentMethod = x
            else:
                raise ValueError("Duplicate method declaration.")

        elif self.state == 2:
            if x == "(":
                self.state = 3

        elif self.state == 3:
            if x == ")":
                self.state = 6
            else:
                if x in ACCEPTED_TYPES:
                    self.currentType = x
                    self.state = 4
                else:
                    raise ValueError("ya goof'd")

        elif self.state == 4:
            if x not in self.vars:
                self.methodVars = x
                self.state = 5
                self.stackOffset += 4
            else:
                raise ValueError("Duplicate variable declaration")

        elif self.state == 5:
            if x == ",":
                self.state = 3
            elif x == ")":
                self.state = 6

        elif self.state == 6:
            if x == "{":
                self.state = 7
                print(self.currentMethod + ":")
            elif x == ";":
                self.functionPrototypes.append(x)

            print("MOV end $S")
            print("MOV $S2 $S")
            print("SUB #" + str(self.stackOffset) + " $S2")

    def parseContent(self, x, output):

        # initial declaration of variable type, return, or function call
        if self.state == 7:
            if x in self.vars:
                self.state = 9
                self.currentVar = x
            elif x in ACCEPTED_TYPES:
                self.state = 8
            elif x in self.methodList:
                self.state = 12
                self.currentVar = x
            elif x in self.functionPrototypes:
                self.state = 12
                self.currentVar = x
            elif x == "}":
                self.state = 0
                self.currentVar = ""
                self.currentType = ""
                self.mathFunction = ""
                self.varLocation.clear()
                self.varValues.clear()
                self.varTypes.clear()
                self.operandCount = 0

        # declaration of variable name
        elif self.state == 8:
            if (x not in self.vars) and (x not in self.methodVars):
                self.vars.append(x)
                self.currentVar = x
                self.varTypes[x] = self.currentType
                self.varLocation[x] = self.memloc
                self.memloc += 4
                self.state = 9

        # end of statement or beginning of assignment to variable
        elif self.state == 9:
            if x == ";":
                self.state = 7
            elif x == "=":
                self.state = 10

        # operand for math formula
        elif self.state == 10:
            self.mathFunction += str(x) + " "
            self.operandCount += 1
            self.state = 11

        # end of math statement or new operator found
        elif self.state == 11:
            if x in OPERATORS:
                self.mathFunction += str(x) + " "
                self.state = 10
            elif x == ";":
                tokens = tokenize(self.mathFunction)
                postfix = in2postfix(tokens)
                result = calc_postfix(postfix, self.varValues, self.varLocation, self.methodVars)
                if self.operandCount == 1:
                    print("MOV #" + str(result) + " $A")
                    print("MEMW [4] $A #" + str(self.varLocation[self.currentVar]))
                else:
                    print("MEMW [4] $D #" + str(self.varLocation[self.currentVar]))
                    print("XOR $D $D")
                self.varValues[self.currentVar] = result
                self.currentVar = ""
                self.currentType = ""
                self.mathFunction = ""
                self.state = 7
                self.operandCount = 0

        # Beginning of function call
        elif self.state == 12:
            if x == "(":
                self.state = 13

        # end of function call, or new argument
        elif self.state == 13:
            if x == ")":
                self.state = 14
            elif x in self.vars:
                print("PUSH #" + self.varLocation[x])
            elif x == ",":
                pass

        # end of function call statement
        elif self.state == 14:
            if x == ";":
                print("CALL " + self.currentVar)
                self.state = 7