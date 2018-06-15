#!/usr/bin/env python

class CompilerTest:

    state = 0
    masterText = ""
    memoryStart = 0x40000000
    varlist = []
    varvalues = {}
    operators = ["=", "+", "-", "*", "/"]

    def parseText(self, text):

        file = open(text, mode="r")
        line = file.readlines()
        output = open("output.txt", mode="w")
        for x in line:
            self.masterText += self.readLine(x, output)

    def readLine(self, line, output):

        if self.state == 0:
            output.write(self.STATE0(line))

    def STATE0(self, line):








