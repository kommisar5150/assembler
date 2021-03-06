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

        # CALL instruction
        elif line[0] == "CALL":
            word = line[1]

            if word[0] == "#":
                word = word[1:]
                instruction += "10000010"
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)
                offset = 5

            elif word[0] == "$":
                word = word[1:]
                instruction += "01110010"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += "0000"
                instruction += str(word)
                offset = 2

            else:  # assume it's a symbol
                instruction += "10000010"
                instruction += str(word)
                offset = 5

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
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "10011010"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

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
            offset = 1

        # DIV instruction
        elif line[0] == "DIV":
            word = line[1]

            if word[0] == "$":
                word = word[1:]
                instruction += "10010101"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2
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
            offset = 1

        # INT instruction
        elif line[0] == "INT":
            word = line[1]

            if word[0] == "#":
                word = word[1:]
                instruction += "10000011"
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)
                offset = 5

            elif word[0] == "$":
                word = word[1:]
                instruction += "01110110"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += "0000"
                instruction += str(word)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

        # JMP instruction
        elif line[0] == "JMP":
            temp = ""  # This will hold the binary instruction of the second argument
            e, l, h, flag = "0", "0", "0", "0"  # Flag initial value
            word = line[2]
            padding = ""

            # since instruction relies on argument after flags, we evaluate this first
            if word[0] == "#":
                word = word[1:]
                instruction += "01000001"
                word = self.translateTextImmediateToImmediate(word)
                temp = '{0:032b}'.format(word)
                padding = "0000"
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "01010001"
                temp = self.translateRegisterNameToRegisterCode(word)
                offset = 2

            else:  # assume it's a symbol
                instruction += "01000001"
                temp = word
                padding = "0000"
                offset = 6

            word = line[1]

            if word[0] == "<" and word[-1] == ">":
                word = word[1:-1]  # remove brackets and evaluate what's in the middle
                word = word.lower()
                if len(word) < 4 or len(word) == 0:
                    for flagvalue in word:
                        if flagvalue == "E":
                            e = "1"
                        elif flagvalue == "L":
                            l = "1"
                        elif flagvalue == "H":
                            h = "1"
                        else:
                            raise ValueError("Invalid operation format")
                else:
                    raise ValueError("Invalid operation format")

                flag = flag + e + l + h  # Concatenate results together to give flag value
            else:
                raise ValueError("Invalid operation format")

            instruction = instruction + padding + flag + temp

        # JMPR instruction
        elif line[0] == "JMPR":
            temp = ""  # This will hold the binary instruction of the second argument
            e, l, h, flag = "0", "0", "0", "0"  # Flag initial value
            word = line[2]
            padding = ""

            # since instruction relies on argument after flags, we evaluate this first
            if word[0] == "#":
                word = word[1:]
                instruction += "01000000"
                word = self.translateTextImmediateToImmediate(word)
                temp = '{0:032b}'.format(word)
                padding = "0000"
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "01010000"
                temp = self.translateRegisterNameToRegisterCode(word)
                offset = 2

            else:  # Unlike JMP, we can't have a label since the value must be an offset
                raise ValueError("Invalid operation format")

            word = line[1]

            if word[0] == "<" and word[-1] == ">":
                word = word[1:-1]  # remove brackets and evaluate what's in the middle
                if len(word) < 4:
                    for flagvalue in word:
                        if flagvalue == "E":
                            e = "1"
                        elif flagvalue == "L":
                            l = "1"
                        elif flagvalue == "H":
                            h = "1"
                        else:
                            raise ValueError("Invalid operation format")

                else:
                    raise ValueError("Invalid operation format")

                flag = flag + e + l + h  # Concatenate results together to give flag value
            else:
                raise ValueError("Invalid operation format")

            instruction = instruction + padding + flag + temp

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
                instruction += "00000001"
                word = self.translateTextImmediateToImmediate(word)
                source = '{0:032b}'.format(word)
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "00010000"
                source = self.translateRegisterNameToRegisterCode(word)
                padding = "0000"
                offset = 3

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
                dest = self.translateRegisterNameToRegisterCode(word)

            else:
                raise ValueError("Invalid operation format")

            if instruction == "00000001":  # insImmReg
                instruction = instruction + width + dest + source
            else:  # insRegReg
                instruction = instruction + width + source + padding + dest

        # MEMW instruction -- This one might be a bit of a mess due to multiple cases
        elif line[0] == "MEMW":

            width = line[1]
            arg1 = line[2]  # Source
            arg2 = line[3]  # Destination
            potential_values = ["1", "2", "3", "4"]  # Width may only be one of these values
            padding = "0000"

            if arg1[0] == "$" and arg2[0] == "$":  # Both arguments are registers
                instruction += "00010001"
                offset = 3
            elif arg1[0] == "$" and arg2[0] == "#":  # Write value in register to immediate address
                instruction += "00100000"
                offset = 6
            elif arg1[0] == "#" and arg2[0] == "$":  # Write value of immediate to address in register
                instruction += "00000000"
                offset = 6
            elif arg1[0] == "#" and arg2[0] == "#":  # Write value of immediate to immediate address
                instruction += "00110000"
                offset = 10
            else:
                raise ValueError("Invalid operation format")

            # Parse info from arguments to assemble instruction
            if arg1[0] == "$":
                arg1 = arg1[1:]
                arg1 = self.translateRegisterNameToRegisterCode(arg1)
            if arg2[0] == "$":
                arg2 = arg2[1:]
                arg2 = self.translateRegisterNameToRegisterCode(arg2)
            if arg1[0] == "#":
                arg1 = arg1[1:]
                arg1 = self.translateTextImmediateToImmediate(arg1)
                arg1 = '{0:032b}'.format(arg1)
            if arg2[0] == "#":
                arg2 = arg2[1:]
                arg2 = self.translateTextImmediateToImmediate(arg2)
                arg2 = '{0:032b}'.format(arg2)

            # Get width info
            if width[0] == "[" and width[-1] == "]":
                width = width[1:-1]  # remove brackets and evaluate what's in the middle
                if width in potential_values:
                    width = self.translateTextImmediateToImmediate(width)
                    width = '{0:04b}'.format(width)
                else:  # Then either it's an invalid argument or a width not supported
                    raise ValueError("Invalid operation format")

            else:
                raise ValueError("Invalid operation format")

            if instruction == "00010001":  # InsRegReg
                instruction = instruction + width + arg1 + padding + arg2
            elif instruction == "00100000":  # InsRegImm
                instruction = instruction + width + arg1 + arg2
            elif instruction == "00000000":  # InsImmReg
                instruction = instruction + width + arg2 + arg1
            else:  # InsImmImm
                instruction = instruction + padding + width + arg1 + arg2

        # MOV instruction
        elif line[0] == "MOV":
            word = line[1]
            insregreg = 0
            arg1 = 0
            arg2 = 0

            if word[0] == "#":  # immediate value
                instruction += bytes((0b01100000,))
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                print("value before conversion: " + str(word))
                word = word.to_bytes(4, byteorder='big')
                instruction += word
                print("and after conversion: " + str(word))
                offset = 6

            elif word[0] == "$":  # register value
                instruction += bytes((0b10011011,))
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                arg1 = word
                insregreg = 1
                offset = 2

            else:  # assume it's a symbol
                instruction += bytes((0b01100000,))
                instruction += b":" + word.encode("utf-8") + b":"
                offset = 6

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                if insregreg:
                    args = (arg1 << 4) + word
                    instruction += bytes((args,))
                else:
                    instruction += bytes((word,))
            else:
                raise ValueError("Invalid operation format")

        # MUL instruction
        elif line[0] == "MUL":
            word = line[1]
            word2 = line[2]
            instruction += "10010100"

            if word[0] == "$" and word2[0] == "$":
                word = word[1:]
                word2 = word2[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                word2 = self.translateRegisterNameToRegisterCode(word2)
                instruction = instruction + str(word) + str(word2)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

        # NOP instruction
        elif line[0] == "NOP":
            instruction += "11111111"
            offset = 1

        # NOT instruction
        elif line[0] == "NOT":
            instruction += "011100000000"
            word = line[1]

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2
            else:
                raise ValueError("Invalid operation format")

        # OR instruction
        elif line[0] == "OR":
            word = line[1]

            if word[0] == "#":  # immediate value
                instruction += "01100010"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)
                offset = 6

            elif word[0] == "$":  # register value
                instruction += "10011000"
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # POP instruction
        elif line[0] == "POP":
            word = line[1]
            instruction += "011101000000"

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2
            else:
                raise ValueError("Invalid operation format")

        # PUSH instruction
        elif line[0] == "PUSH":
            word = line[1]

            if word[0] == "#":  # immediate value
                instruction += "10000001"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                instruction += str(word)
                offset = 5

            elif word[0] == "$":  # register value
                instruction += "011100110000"
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

            else:  # assume it's a symbol
                instruction += "10000001"
                instruction += str(word)
                offset = 5

        # RET instruction
        elif line[0] == "RET":
            instruction += "11110000"
            offset = 1

        # STSTOR instruction
        elif line[0] == "SFSTOR":
            temp = ""  # This will hold the binary instruction of the second argument
            e, l, h, flag = "0", "0", "0", "0"  # Flag initial value
            word = line[2]
            padding = ""

            # since instruction relies on argument after flags, we evaluate this first
            if word[0] == "#":
                word = word[1:]
                instruction += "01000010"
                word = self.translateTextImmediateToImmediate(word)
                temp = '{0:032b}'.format(word)
                padding = "0000"
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "01010010"
                temp = self.translateRegisterNameToRegisterCode(word)
                offset = 2

            else:  # assume it's a symbol
                instruction += "01000010"
                temp = word
                offset = 6

            word = line[1]

            if word[0] == "<" and word[-1] == ">":
                word = word[1:-1]  # remove brackets and evaluate what's in the middle
                word = word.lower()
                if len(word) < 4 or len(word) == 0:
                    for flagvalue in word:
                        if flagvalue == "E":
                            e = "1"
                        elif flagvalue == "L":
                            l = "1"
                        elif flagvalue == "H":
                            h = "1"
                        else:
                            raise ValueError("Invalid operation format")
                else:
                    raise ValueError("Invalid operation format")

                flag = flag + e + l + h  # Concatenate results together to give flag value
            else:
                raise ValueError("Invalid operation format")

            instruction = instruction + padding + flag + temp

        # SIVR instruction
        elif line[0] == "SIVR":
            word = line[1]
            instruction += "011101010000"

            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2
            else:
                raise ValueError("Invalid operation format")

        # SHL instruction
        elif line[0] == "SHL":
            word = line[1]

            if word[0] == "#":
                instruction += "01100101"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "10010110"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register
            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # SHR instruction
        elif line[0] == "SHR":
            word = line[1]

            if word[0] == "#":
                instruction += "01100100"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "10011001"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register
            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # SNT instruction
        elif line[0] == "SNT":
            None

        # SUB instruction
        elif line[0] == "SUB":
            word = line[1]

            if word[0] == "#":
                instruction += "01100111"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "10010011"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register
            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
            else:
                raise ValueError("Invalid operation format")

        # XOR instruction
        elif line[0] == "XOR":
            word = line[1]

            if word[0] == "#":
                instruction += "01100011"
                word = word[1:]
                word = self.translateTextImmediateToImmediate(word)
                word = '{0:032b}'.format(word)
                word += "0000"
                instruction += str(word)
                offset = 6

            elif word[0] == "$":
                word = word[1:]
                instruction += "10010000"
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
                offset = 2

            else:
                raise ValueError("Invalid operation format")

            word = line[2]  # check second value to be sure it's a register
            if word[0] == "$":
                word = word[1:]
                word = self.translateRegisterNameToRegisterCode(word)
                instruction += str(word)
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
