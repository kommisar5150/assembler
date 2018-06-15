#!/usr/bin/env python

from constants import ACCEPTED_TYPES, \
                      OPERATORS

class CompilerTest:
    """
    STATE 0 = Function declaration
    STATE 1 = Within function, reset to 0 upon }
    """
    state = 0
    globalCounter = 0
    masterText = ""
    memoryStart = 0x40000000
    varlist = []
    varvalues = {}
    methodStatements = []
    methodList = {}
    operators = ["=", "+", "-", "*", "/"]

    def parseText(self, text):

        file = open(text, mode="r")
        line = file.readlines()
        output = open("output.txt", mode="w")
        for x in line:
            self.readLine(x, output)

    def readLine(self, line, output):

        if self.state < 5:
            self.parseMethodHeader(line)
        else:
            self.parseMethodContents(line)

    def parseMethodHeader(self, line):
        argList = []
        methodName = ""
        methodType = ""
        argName = ""
        argType = ""
        expectToken = 0

        for x in line:

            if self.state == 0 and x != "\n":
                if x == " " and expectToken == 1:
                    if methodType not in ACCEPTED_TYPES:
                        raise ValueError("data return type not valid for function")
                    self.state += 1
                    expectToken = 0
                elif x == " " and expectToken == 0:
                    pass
                else:
                    methodType += x
                    expectToken = 1

            elif self.state == 1:
                if x == "(":
                    self.state += 1
                    expectToken = 0
                else:
                    if x != " " and expectToken == 0:
                        methodName += x
                    elif expectToken == 1:
                        raise ValueError("Expected \"(\", got " + x)
                    else:
                        expectToken = 1

            elif self.state == 2:
                if x == ")":
                    if argType not in ACCEPTED_TYPES and argType != "":
                        raise ValueError("data type not valid for argument : " + argType)
                    self.state = 4
                elif x == " " and expectToken != 2:
                    self.state = 3
                else:
                    if expectToken == 0:
                        argType += x
                    if expectToken == 2 and x != " ":
                        argType += x
                        expectToken = 0

            elif self.state == 3:
                if x == ")":
                    self.state = 4
                    argList.append((argType, argName))
                    argType, argName = "", ""
                    expectToken = 0
                else:
                    if x != " " and expectToken == 0 and x != ",":
                        argName += x
                    elif x == ",":
                        self.state = 2
                        argList.append((argType, argName))
                        argType, argName = "", ""
                        expectToken = 2
                    elif expectToken == 1:
                        raise ValueError("Expected \")\", got " + x)
                    else:
                        expectToken = 1

            elif self.state == 4:
                if x != "{":
                    raise ValueError("Expected \"{\", got " + x)
                else:
                    if methodType != "" and methodName != "":
                        self.methodList[methodName] = (methodType, argList)
                        print(methodName)
                        print(methodType)
                        print(argList)
                    self.state = 5

            elif self.state == 5:  # In case of an empty body on the same line
                if x == "}":
                    self.state = 0



    def parseMethodContents(self, line):
        varType = ""
        varName = ""
        lineStatement = ""
        expectedToken = 0
        charpos = 0

        for x in line:
            if self.state == 5:
                if x == "\n":
                    pass
                elif x == "}":
                    self.state = 0

                elif x == " " and expectedToken == 1:
                    self.state = 6
                    expectedToken = 0
                    print(varType)
                elif x != " ":
                    varType += x
                    expectedToken = 1
                else:
                    pass  # Just a space before variable type declaration

            if self.state == 6:
                if varType in ACCEPTED_TYPES:
                    if x != ";" and x != " ":
                        varName += x
                        expectedToken = 1
                    elif x == " " and expectedToken == 1:
                        self.state = 7
                        expectedToken = 0
                    elif x == ";":
                        print(varName)
                        self.varvalues[varName] = 0
                        self.state = 5

            elif self.state == 7:
                if x == " ":
                    pass
                elif x == ";":
                    self.state = 5
                elif x == "=":
                    self.state = 8

            elif self.state == 8:
                if x == " " and expectedToken == 0:
                    pass
                elif x in OPERATORS:
                    self.varvalues[varName] = self.math(line[charpos:])

            charpos += 1

    def math(self, line):
        return " "
