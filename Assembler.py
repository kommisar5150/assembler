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

class Assembler:

    def __init__(self, inputFile=None, outputFile=None):

        '''

        This block sorts out the internal and external symbols, and adds them to the
        output string.

        :param inputFile:
        :param outputFile:
        '''

        build = instructionBuilder()
        masterString = ""  # String that will eventually be our output file
        info = os.stat(inputFile)
        size = info.st_size

        # variables used to assemble file.
        masterString += "<AssemblySize>" + str(size) + "</AssemblySize>\n\n"
        global_list = []
        external_list = []
        internal_list = []
        file = open(inputFile, mode="r")
        file_lines = file.readlines()
        file.close()
        file = open(inputFile, mode="r")
        f = file.read()
        file.close()

        # pattern matching to find global functions (external symbols)
        globalvars = re.findall(r"\.global\s[\w.-]+\n", f)
        for word in globalvars:
            word = word[8:-1]
            global_list.append(word)

        # pattern matching to find ALL symbols. If symbol is in global function list, add to external list.
        # otherwise, add to internal list.
        match = re.findall(r'[\w.-]+:\n', f)
        for word in match:
            word = word[:-2]
            if word in global_list:
                external_list.append(word)
            else:
                internal_list.append(word)

        # builds the output file by extracting and printing each symbol into its appropriate category.
        masterString += "<ExternalSymbols>\n"
        for word in external_list:
            masterString += "\t<refName>" + word + "</refName>\n"

        masterString += "\n<InternalSymbols>\n"
        for word in internal_list:
            masterString += "\t<refName>" + word + "</refName>\n"


        '''
        This block reads each line and determines if an instruction has been found.
        
        
        '''
        masterString += "<Text>\n"
        for line in file_lines:
            if line[0] != "\n":
                masterString += "\n" + line
                line = line.split()
                print(line)
                if line is not None:
                    instruction = build.build(line)
                    if instruction is not None:
                        masterString += instruction + "\n"

        masterString += "\n</Text>"
        print(external_list)
        print(internal_list)
        file = open(outputFile, mode="w")
        file.write(masterString)
        file.close()

