#!/usr/bin/python -tt

from Assembler import Assembler
from instructionBuilder import instructionBuilder

def main():
    assembler = Assembler("testcase.casm", "test.o")


if __name__ == '__main__':
    main()
