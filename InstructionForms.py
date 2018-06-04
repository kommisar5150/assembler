#!/usr/bin/env python

"""
This file contains all potential states of an instruction. The parser gathers info about the instruction and arguments.
The arguments are identified as either registers, immediate values, flags, or width. These idenfitications are then
concatenated together as a "state" string. Because instructions may contain multiple forms, these states ensure that
each instruction code is unique for each form.

Ex: MOV $A $B is of the form Instruction - Register - Register. In this scheme, it would be "State 2".
MOV could also be Instruction - Immediate - Register, so within the STATE2 list, the MOV entry has the correct
binary value that we need for this line of code.
"""

# INS
STATE0 = [("RET", 0b11110000, 1), ("ACTI", 0b11110001, 1), ("DACTI", 0b11110010, 1), ("HIRET", 0b11110011, 1),
          ("NOP", 0b11111111, 1)]

# INSREG
STATE1 = [("CALL", 0b01110010, 2), ("INT", 0b10000011, 2), ("NOT", 0b01110000, 2), ("POP", 0b01110100, 2),
          ("PUSH", 0b01110011, 2), ("SIVR", 0b01110101, 2), ("SNT", 0b01110001, 2)]

# INSREGREG
STATE2 = [("ADD", 0b10010010, 2), ("AND", 0b10010111, 2), ("CMP", 0b10011010, 2), ("DIV", 0b10010101, 2),
          ("MOV", 0b10011011, 2), ("MUL", 0b10010100, 2), ("OR", 0b10011000, 2), ("SHL", 0b10010110, 2),
          ("SHR", 0b10011001, 2), ("SUB", 0b10010011, 2), ("XOR", 0b10010000, 2)]

# INSIMM
STATE3 = [("CALL", 0b10000010, 5), ("INT", 0b01110110, 5), ("PUSH", 0b10000001, 5), ("SNT", 0b10000000, 5)]

# INSIMMREG
STATE4 = [("ADD", 0b01100110, 6), ("AND", 0b01100001, 6), ("CMP", 0b01101000, 6), ("MOV", 0b01100000, 6),
          ("OR", 0b01100010, 6), ("SHL", 0b01100101, 6), ("SHR", 0b01100100, 6), ("SUB", 0b01100111, 6),
          ("XOR", 0b01100011, 6)]

# INSWIDTHIMMIMM
STATE5 = [("MEMW", 0b00110000, 10)]

# INSWIDTHIMMREG
STATE6 = [("MEMR", 0b00000001, 6), ("MEMW", 0b00000000, 6)]

# INSWIDTHREGIMM
STATE7 = [("MEMW", 0b00100000, 6)]

# INSWIDTHREGREG
STATE8 = [("MEMR",  0b00010000, 3), ("MEMW", 0b00010001, 3)]

# INSFLAGIMM
STATE9 = [("JMP", 0b01000001, 6), ("JMPR", 0b01000000, 6), ("SFSTOR", 0b01000010, 6)]

# INSFLAGREG
STATE10 = [("JMP", 0b01010001, 2), ("JMPR", 0b01010000, 2), ("SFSTOR", 0b01010010, 2)]

INSTRUCTION_LIST = ["ACTI", "ADD", "AND", "CALL", "CMP", "DACTI", "DIV", "HIRET",
                    "INT", "JMP", "JMPR", "MEMR", "MEMW", "MOV", "MUL", "NOP", "NOT", "NOP",
                    "OR", "POP", "PUSH", "RET", "SFSTOR", "SIVR", "SHL", "SHR", "SUB", "XOR"]

IDENTIFIER_LIST = [":", ".GLOBAL", ".DATAALPHA", ".DATANUMERIC", ".DATAMEMREF", ";"]

