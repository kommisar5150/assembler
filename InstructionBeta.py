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
import struct

__author__ = "CSE"
__copyright__ = "Copyright 2018, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"



class instructionBuilder:

    relativeAddressCounter = 0

    def build(self, text):

        text = text.upper()
        line = text.split()
        instruction = b""
        offset = 0
        data_identifier = line[0]  # used for special identifiers such as .dataAlpha, comments etc.

        # first off, we need to determine if this line has a label or global label to be referenced
        if data_identifier[-1] == ":":
            label = data_identifier[:-1]
            return label, self.relativeAddressCounter, 1

        elif data_identifier == ".GLOBAL":
            label = line[1]
            return label, self.relativeAddressCounter, 2

        # ACTI instruction
        elif line[0] == "ACTI":
            instruction += bytes((0b11110001,))
            offset = 1

        # ADD instruction
        elif line[0] == "ADD":
            word = line[1]
            insregreg = 0

            if word[0] == "#":
                instruction += bytes((0b01100110,))
                arg1 = word[1:]
                arg1 = self.translateTextImmediateToImmediate(arg1)
                arg1 = arg1.to_bytes(4, byteorder='big')
                offset = 6

            elif word[0] == "$":
                arg1 = word[1:]
                instruction += bytes((0b10010010,))
                arg1 = self.translateRegisterNameToRegisterCode(arg1)
                insregreg = 1
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register
            if word[0] == "$":
                arg2 = word[1:]
                arg2 = self.translateRegisterNameToRegisterCode(arg2)
                if insregreg:
                    args = (arg1 << 4) + arg2
                    instruction += bytes((args,))
                else:
                    instruction += arg1 + bytes((arg2,))

            else:
                raise ValueError("Invalid operation format")

        # AND instruction
        elif line[0] == "AND":
            word = line[1]
            insregreg = 0

            if word[0] == "#":
                word = word[1:]
                instruction += bytes((0b01100001,))
                arg1 = self.translateTextImmediateToImmediate(word)
                arg1 = arg1.to_bytes(4, byteorder='big')
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += bytes((0b10010111,))
                arg1 = self.translateRegisterNameToRegisterCode(word)
                insregreg = 1
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                arg2 = self.translateRegisterNameToRegisterCode(word)

                if insregreg:
                    args = (arg1 << 4) + arg2
                    instruction += bytes((args,))
                else:
                    instruction += arg1 + bytes((arg2,))
            else:
                raise ValueError("Invalid operation format")

        elif data_identifier[0] == ";":
            pass  # it's just a comment

        elif line[0] == ".DATAALPHA":
            line = line[1:]
            line = " ".join(line)
            instruction += line.encode("utf-8")
            offset = len(instruction) + 1
            instruction += b"\x00"
            print(instruction)
            print(offset)

        elif line[0] == ".DATANUMERIC":
            instruction += str(line[1])
            offset = 4

        elif line[0] == ".DATAMEMREF":
            instruction += str(line[1])
            offset = 4

        else:
            raise ValueError("Invalid operation format")

        # Add the calculated offset of the current instruction to cumulative length of file
        self.relativeAddressCounter += offset

        return instruction, self.relativeAddressCounter, 0

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
        registerCode = registerCode & 0xFF
        return registerCode
