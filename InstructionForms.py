#!/usr/bin/env python

STATE0 = [("RET", 0b11110000, 1), ("ACTI", 0b11110001, 1), ("DACTI", 0b11110010, 1), ("HIRET", 0b11110011, 1),
          ("NOP", 0b11111111, 1)]
STATE1 = []
STATE2 = [("ADD", 0b10010010, 2), ("AND", 0b10010111, 2), ("CMP", 0b10011010, 2), ("DIV", 0b10010101, 2),
          ("MOV", 0b10011011, 2), ("MUL", 0b10010100, 2), ("OR", 0b10011000, 2), ("SHL", 0b10010110, 2)]
STATE3 = []
STATE4 = []
STATE5 = []
STATE6 = []
STATE7 = []
STATE8 = []
STATE9 = []
STATE10 = []

INSTRUCTION_LIST = ["ACTI", "ADD", "AND", "CALL", "CMP", "DACTI", "DIV", "HIRET",
                    "INT", "JMP", "JMPR", "MEMR", "MEMW", "MUL", "NOP", "NOT", "NOP",
                    "OR", "POP", "PUSH", "RET", "SFSTOR", "SIVR", "SHL", "SHR", "SUB", "XOR"]

INDICATOR_LIST = [".GLOBAL", ".DATAALPHA", ".DATANUMERIC", ".DATAMEMREF", ":", ";"]
