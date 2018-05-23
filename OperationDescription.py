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

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"

"""
The point of this is to keep the ExecutionUnit code clean so we don't have to deal directly
with binary code for instruction selection inside of the execution unit.
"""

operationDescription = {
    "ACTI": [0b11110001],
    "ADD": [0b01100110, 0b10010010],
    "AND": [0b01100001, 0b10010111],
    "CALL": [0b10000010, 0b01110010],
    "CMP": [0b01101000, 0b10011010],
    "DACTI": [0b11110010],
    "DIV": [0b10010101],
    "HIRET": [0b11110011],
    "INT": [0b01110110, 0b10000011],
    "JMP": [0b01000001, 0b01010001],
    "JMPR": [0b01000000, 0b01010000],
    "MEMR": [0b00000001, 0b00010000],
    "MEMW": [0b00110000, 0b00000000, 0b00100000, 0b00010001],
    "MOV": [0b01100000, 0b10011011],
    "MUL": [0b10010100],
    "NOP": [0b11111111],
    "NOT": [0b01110000],
    "OR": [0b01100010, 0b10011000],
    "POP": [0b01110100],
    "PUSH": [0b10000001, 0b01110011],
    "RET": [0b11110000],
    "SFSTOR": [0b01000010, 0b01010010],
    "SIVR": [0b01110101],
    "SHL": [0b01100101, 0b10010110],
    "SHR": [0b01100100, 0b10011001],
    "SNT": [0b10000000, 0b01110001],  # Not implemented at current time, DO NOT USE
    "SUB": [0b01100111, 0b10010011],
    "XOR": [0b01100011, 0b10010000]
}
