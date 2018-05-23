#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2018  CSE

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os
import re
from OperationDescription import operationDescription
from Constants import REGISTER_PREFIX, \
                      IMMEDIATE_PREFIX, \
                      WIDTH_INDICATORS, \
                      FLAGS_INDICATORS, \
                      COMMENT_INDICATORS, \
                      MEMORY_REFERENCE_INDICATORS, \
                      DATA_ALPHA_INDICATOR, \
                      DATA_NUMERIC_INDICATOR, \
                      DATA_MEMORY_REFERENCE, \
                      EXPORTED_REFERENCE_INDICATOR
from Configuration import REGISTER_A, \
                          REGISTER_B, \
                          REGISTER_C, \
                          REGISTER_D, \
                          REGISTER_E, \
                          REGISTER_F, \
                          REGISTER_G, \
                          REGISTER_H, \
                          REGISTER_J, \
                          REGISTER_K, \
                          REGISTER_L, \
                          REGISTER_M, \
                          REGISTER_N, \
                          REGISTER_O, \
                          REGISTER_P, \
                          REGISTER_S

__author__ = "CSE"
__copyright__ = "Copyright 2018, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"


class instructionBuilder:

    def build(self, line):
        instruction = ""

        # if the instruction is MOV
        if line[0] == "MOV":
            word = line[1]

            if word[0] == "#":  # immediate value
                instruction += "01100000"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)

            elif word[0] == "$":  # register value
                instruction += "10011011"
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)

            else:  # assume it's a symbol
                instruction += "01100000"
                instruction += str(word)

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # ACTI instruction
        if line[0] == "ACTI":
            instruction += "11110001"

        # ADD instruction
        elif line[0] == "ADD":
            word = line[1]

            if word[0] == "#":
                instruction += "01100110"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "10010010"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register
            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # AND instruction
        elif line[0] == "AND":
            word = line[1]

            if word[0] == "#":
                word = word[1:]
                instruction += "01100001"
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "10010111"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # CALL instruction
        elif line[0] == "CALL":
            word = line[1]

            if word[0] == "#":
                word = word[1:]
                instruction += "10000010"
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "01110010"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)

            else:  # assume it's a symbol
                instruction += "10000010"
                instruction += str(word)

        # CMP instruction
        elif line[0] == "CMP":
            word = line[1]

            if word[0] == "#":
                word = word[1:]
                instruction += "01101000"
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "10011010"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # DACTI instruction
        elif line[0] == "DACTI":
            instruction += "11110010"

        # DIV instruction
        elif line[0] == "DIV":
            word = line[1]

            if word[0] == "$":
                word = word[1:]
                instruction += "10010101"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # HIRET instruction
        elif line[0] == "HIRET":
            instruction += "11110011"

        # INT instruction
        elif line[0] == "INT":
            word = line[1]

            if word[0] == "#":
                word = word[1:]
                instruction += "10000011"
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "01110110"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)

            else:
                raise ValueError("Invalid operation format")

        # JMP instruction
        elif line[0] == "JMP":
            temp = ""  # This will hold the binary instruction of the second argument
            e, l, h, flag = "0", "0", "0", "0"  # Flag initial value
            word = line[2]

            # since instruction relies on argument after flags, we evaluate this first
            if word[0] == "#":
                word = word[1:]
                instruction += "01000001"
                word = self.translateTextImmediateToImmediate(word)
                temp = '{0:032b}'.format(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "01010001"
                temp = self.translateRegisterNameToRegisterCode(word)

            else:  # assume it's a symbol
                instruction += "01000001"
                temp = word

            word = line[1]

            if word[0] == "<" and word[-1] == ">":
                word = word[1:-1]  # remove brackets and evaluate what's in the middle
                word = word.lower()
                if len(word) < 4 or len(word) == 0:
                    for flag in word:
                        if flag == "e":
                            e = "1"
                        elif flag == "l":
                            l = "1"
                        elif flag == "h":
                            h = "1"
                        else:
                            raise ValueError("Invalid operation format")
                else:
                    raise ValueError("Invalid operation format")

                flag = flag + e + l + h  # Concatenate results together to give flag value
            else:
                raise ValueError("Invalid operation format")

            instruction = instruction + "0000" + flag + temp

        # JMPR instruction
        elif line[0] == "JMPR":
            temp = ""  # This will hold the binary instruction of the second argument
            e, l, h, flag = "0", "0", "0", "0"  # Flag initial value
            word = line[2]

            # since instruction relies on argument after flags, we evaluate this first
            if word[0] == "#":
                word = word[1:]
                instruction += "01000001"
                word = self.translateTextImmediateToImmediate(word)
                temp = '{0:032b}'.format(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "01010001"
                temp = self.translateRegisterNameToRegisterCode(word)

            else:  # Unlike JMP, we can't have a label since the value must be an offset
                raise ValueError("Invalid operation format")

            word = line[1]

            if word[0] == "<" and word[-1] == ">":
                word = word[1:-1]  # remove brackets and evaluate what's in the middle
                if len(word) < 4:
                    for flag in word:
                        if flag == "e":
                            e = "1"
                        elif flag == "l":
                            l = "1"
                        elif flag == "h":
                            h = "1"
                        else:
                            raise ValueError("Invalid operation format")

                else:
                    raise ValueError("Invalid operation format")

                flag = flag + e + l + h  # Concatenate results together to give flag value
            else:
                raise ValueError("Invalid operation format")

            instruction = instruction + "0000" + flag + temp

        # MEMR instruction
        elif line[0] == "MEMR":

            source = ""  # This will hold the binary value of the source to be read from
            dest = ""  # This will hold the binary value of the destination to hold the read value (must be register)
            width = ""  # Will contain the width, or bytes to be read from source
            padding = ""  # If it's an insregreg instruction, we need to pad with 4 zeroes to fill in byte
            potential_values = ["1","2","3","4"]  # Width may only be one of these values

            word = line[2]  # Source value

            # since instruction relies on argument after width, we evaluate this first
            if word[0] == "#":
                word = word[1:]
                instruction += "01000001"
                word = self.translateTextImmediateToImmediate(word)
                source = '{0:032b}'.format(word)

            elif word[0] == "$":
                word = word[1:]
                instruction += "01010001"
                source = self.translateRegisterNameToRegisterCode(word)
                padding = "0000"

            else:
                raise ValueError("Invalid operation format")

            word = line[1]  # Width value

            # Evaluate width argument
            if word[0] == "[" and word[-1] == "]":
                word = word[1:-1]  # remove brackets and evaluate what's in the middle
                if word in potential_values:
                    word = self.translateTextImmediateToImmediate(word)
                    width = '{0:04b}'.format(word)
                else:  # Then either it's an invalid argument or a width not supported
                    raise ValueError("Invalid operation format")

            else:
                raise ValueError("Invalid operation format")

            word = line[3]  # Destination value (can only be a register)

            if word[0] == "$":
                word = word[1:]
                source = self.translateRegisterNameToRegisterCode(word)

            else:
                raise ValueError("Invalid operation format")

            instruction = instruction + width + dest + padding + source

        elif line[0] == "MEMW":
            None
        elif line[0] == "MUL":
            None
        elif line[0] == "NOP":
            None
        elif line[0] == "NOT":
            None
        elif line[0] == "OR":
            None
        elif line[0] == "POP":
            None
        elif line[0] == "PUSH":
            None
        elif line[0] == "RET":
            None
        elif line[0] == "SFSTOR":
            None
        elif line[0] == "SIVR":
            None
        elif line[0] == "SHL":
            None
        elif line[0] == "SHR":
            None
        elif line[0] == "SNT":
            None
        elif line[0] == "SUB":
            None
        elif line[0] == "XOR":
            None
        else:
            print("maybe comment or label")
            # raise ValueError("Invalid operation format")

        return instruction

    def translateTextImmediateToImmediate(self, textImmediate: str=""):
        """
        This will translate an immediate value in a way that can be understood by the architecture.
        :param textImmediate: str, an immediate value to be translated
        :return: int, an immediate that can be worked on
        """
        print(textImmediate)

        immediate = None
        isNegative = False
        textImmediate = textImmediate.lower()  # Needed in case of 0XFF instead of 0xFF

        if textImmediate[0] == "-":
            isNegative = True
            textImmediate = textImmediate[1:]

        if len(textImmediate) > 2 and textImmediate[0:2] == "0b":
            # Indicates binary immediate
            baseToUse = 2
            textImmediate = textImmediate[2:]
        elif len(textImmediate) > 2 and textImmediate[0:2] == "0x":
            # Indicate hexadecimal immediate
            baseToUse = 16
            textImmediate = textImmediate[2:]
        else:
            # Take a leap of faith! This should be base 10
            baseToUse = 10

        immediate = int(textImmediate, baseToUse)

        validationImmediate = immediate
        immediate &= 0xFFFFFFFF  # Maximum immediate value is 32 bits

        if validationImmediate != immediate:
            raise ValueError("Given immediate value is too big, {} received but maxim value is 0xFFFFFFFF".format(hex(validationImmediate)))

        # If number was negative, get the 2 complement for this number
        if isNegative:
            immediate ^= 0xFFFFFFFF  # Flips all the bits, yield the 1 complement
            immediate += 1  # 1 complement + 1 gives the 2 complement
            immediate &= 0xFFFFFFFF  # Trim down to acceptable size!

        return immediate

    def translateRegisterNameToRegisterCode(self, registerName: str=""):
        """
        This takes a register name and returns a register code as per:
            A = 0x00
            B = 0x01
            C = 0x10
            ...
            S = 0x1111
        Throws error if register is not A, B, C or S
        :param registerName: str, representing the register that needs translation
        :return: int, the int that represents the register
        """
        registerCode = None
        registerName = registerName.upper()

        if registerName == "A":
            registerCode = REGISTER_A
        elif registerName == "B":
            registerCode = REGISTER_B
        elif registerName == "C":
            registerCode = REGISTER_C
        elif registerName == "D":
            registerCode = REGISTER_D
        elif registerName == "E":
            registerCode = REGISTER_E
        elif registerName == "F":
            registerCode = REGISTER_F
        elif registerName == "G":
            registerCode = REGISTER_G
        elif registerName == "H":
            registerCode = REGISTER_H
        elif registerName == "J":
            registerCode = REGISTER_J
        elif registerName == "K":
            registerCode = REGISTER_K
        elif registerName == "L":
            registerCode = REGISTER_L
        elif registerName == "M":
            registerCode = REGISTER_M
        elif registerName == "N":
            registerCode = REGISTER_N
        elif registerName == "O":
            registerCode = REGISTER_O
        elif registerName == "P":
            registerCode = REGISTER_P
        elif registerName == "S":
            registerCode = REGISTER_S
        else:
            raise ValueError("Invalid register provided. '{}' seen as input, expect A, B, C or S.".format(registerName))

        return registerCode

    '''
    def __init__(self):

        test = "MOV $A $B"
        test2 = "MOV #0x4F $A"
        test = test.split()
        test2 = test2.split()
        instruction = self.build(test)
        instruction2 = self.build(test2)
        print(test)
        print(test2)
        print(instruction)
        print(instruction2)
    '''
