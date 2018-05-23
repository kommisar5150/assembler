#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2016  CSE

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

from OperationDescription import operationDescription

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"


class Instruction:
    """
    This class is only used for instruction encapsulation after they are fetched from memory.
    An instance of this class is built by the InstructionFetchUnit and is passed to the
    ExecutionUnit for execution. This class is simply there to help lower the number of
    binary parsing required in the execution of a given instruction. It is also used
    by the Assembler in order to help build the binary code associated with a specific
    instruction.
    """

    instructionCode = None
    sourceRegister = None
    destinationRegister = None
    sourceImmediate = None
    destinationImmediate = None
    width = None
    flags = None
    operationMnemonic = None
    instructionLength = None

    def __init__(self, binaryInstruction=0b000000, form=None, skipValidation=False):
        """
        This allow for initialisation of the instruction by parsing the binary instruction code
        :param binaryInstruction: A big number representing the instruction
        :param form: The form representing the instruction as shown in FormDescription.py
        :return: An instruction! Warning, this instruction could be invalid!
        """

        if not skipValidation:
            self.instructionLength = form["length"]

            # Parse the description so we can initiate the instruction
            for descriptionElement in form["description"]:
                mask = form["description"][descriptionElement]
                extractedBinary = self._extractValueFromBinaryField(mask, binaryInstruction)

                # There is no validation here for performance reason
                # WE RELY ON THE FACT that the form description is correct
                # and does not contain any typo!!!
                setattr(self, descriptionElement, extractedBinary)

            # This will simply get the instruction mnemonic from a list of possible mnemonics
            for instructionMnemonic in operationDescription:
                if self.instructionCode in operationDescription[instructionMnemonic]:
                    self.operationMnemonic = instructionMnemonic
                    break

            if self.operationMnemonic is None:
                raise ValueError("Invalid instruction detected")

        return

    def _extractValueFromBinaryField(self, mask, field):
        """
        This method takes a value and a binary mask. It will extract the part of the value that
        is covered by the mask and return it to the user.
        Example:
            value          = 0b11111111
            mask           = 0b00110000
            result         = 0b00110000
            returned value = 0b11
        :param mask: Binary mask showing what need to be extracted
        :param field: The field from which we want to do the extract
        :return: int, the extracted value
        """

        # First, we get the mask at the right. Looking for mask % 2  will, when = 1
        # tell us that the mask is now fully aligned at the right
        if mask > 0:
            while (mask % 2) != 1:
                mask >>= 1
                field >>= 1

        field &= mask  # The result is the "parsed" value

        return field
