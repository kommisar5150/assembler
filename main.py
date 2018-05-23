#!/usr/bin/python -tt

from Assembler import Assembler
from instructionBuilder import instructionBuilder

def main():
    assembler = Assembler("Hello.casm", "Hello.o")


if __name__ == '__main__':
    main()
