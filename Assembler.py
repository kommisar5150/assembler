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
        global_list = []
        external_list = []
        internal_list = []
        file = open(inputFile, mode="r")
        file_lines = file.readlines()
        file.close()
        file = open(inputFile, mode="r")
        f = file.read()
        file.close()

        '''
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
        '''

        offset = 0
        masterString += "<Text>\n"
        for line in file_lines:
            line = line.upper()
            if line[0] != "\n":
                if line is not None:
                    instruction, offset, label_flag = build.build(line)
                    if label_flag == 0:
                        masterString += instruction + "\n"
                    elif label_flag == 1:
                        label_tuple = (instruction, offset)
                        internal_list.append(label_tuple)
                        if instruction in global_list:
                            external_list.append(label_tuple)
                    elif label_flag == 2:
                        global_list.append(instruction)
                    else:
                        print("Something went horribly wrong")

        masterString += "</Text>"

        # builds the output file by extracting and printing each symbol into its appropriate category.
        xmlstring = "<AssemblySize>" + str(size) + "</AssemblySize>\n<ExternalSymbols>\n"
        for word in external_list:
            xmlstring += "\t<refName>" + word[0] + "</refName>\n"
            xmlstring += "\t<refAdd>" + str(word[1]) + "</refAdd>\n"

        xmlstring += "</ExternalSymbols>\n<InternalSymbols>\n"
        for word in internal_list:
            xmlstring += "\t<refName>" + word[0] + "</refName>\n"
            xmlstring += "\t<refAdd>" + str(word[1]) + "</refAdd>\n"
        xmlstring += "</InternalSymbols>\n"

        '''
        This block reads each line and determines if an instruction has been found.
        
        
        '''
        xmlstring += masterString
        print(external_list)
        print(internal_list)
        file = open(outputFile, mode="w")
        file.write(xmlstring)
        file.close()

