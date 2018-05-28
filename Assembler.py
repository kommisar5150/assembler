#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

import os
import re
from Instruction import Instruction
from instructionBuilder import instructionBuilder
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

class Assembler:

    def __init__(self, inputFile=None, outputFile=None):

        build = instructionBuilder()  # instructionBuilder object which will return the binary code for instructions
        masterString = b""  # String that will eventually be our output file
        xmlstring = b""  # String that will contain the "xml" data at the beginning of the .o file
        global_list = []  # Temporary list to hold the names of global(external) symbols
        external_list = []  # Master list of all external symbols to be used by linker
        internal_list = []  # # Master list of all internal symbols
        offset = 0  # Offset used to calculate a label's offset from the beginning of the file

        file = open(inputFile, mode="r")
        file_lines = file.readlines()
        file.close()


        '''
        This block assembles the binary data itself. It will parse each line individually and extract the info needed:
        1.If the label flag is set to 0, it's a regular instruction, string, number, of memref.
        2.If the label flag is set to 1, it's an internal symbol.
        3.If the label flag is set to 2, it's an external symbol.
        In cases 2 and 3, the symbols are added to their respective lists along with their memory location.
        Memory locations are relative to the beginning of the file. Instructions and data are given set lengths.
        Internal and external symbol lists contain tuples containing the symbol name, and its offset. 
        These will be used to fill the .o file information before the binary data.
        '''

        masterString += b"<Text>"

        for line in file_lines:

            line = line.upper()

            if line[0] != "\n":

                if line is not None:
                    instruction, offset, label_flag = build.build(line)

                    if label_flag == 0:
                        masterString += instruction

                    elif label_flag == 1:
                        label_tuple = (instruction, offset)
                        internal_list.append(label_tuple)
                        if instruction in global_list:
                            external_list.append(label_tuple)

                    elif label_flag == 2:
                        global_list.append(instruction)

                    else:
                        print("Something went horribly wrong")

        masterString += b"</Text>"

        # builds the output file by extracting and printing each symbol into its appropriate category.
        xmlstring = b"<AssemblySize>" + struct.pack(">I", build.relativeAddressCounter) + \
                    b"</AssemblySize><ExternalSymbols>"

        for word in external_list:
            xmlstring += b"<refName>" + word[0].encode("utf-8") + b"</refName>"
            xmlstring += b"<refAdd>" + struct.pack(">I", word[1]) + b"</refAdd>"

        xmlstring += b"</ExternalSymbols><InternalSymbols>"

        for word in internal_list:
            xmlstring += b"<refName>" + word[0].encode("utf-8") + b"</refName>"
            xmlstring += b"<refAdd>" + struct.pack(">I", word[1]) + b"</refAdd>"

        xmlstring += b"</InternalSymbols>"

        # Now we can put the xml string together with the masterString to output to file
        xmlstring += masterString
        print(external_list)
        print(internal_list)
        file = open(outputFile, mode="wb")
        file.write(xmlstring)
        file.close()

