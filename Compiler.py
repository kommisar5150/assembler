#!/usr/bin/env python


'''
This file takes in a simple code and converts it to capua ASM instructions to be run in the VM.
The goal is to have a simple (x,y) input followed by a string to have text displayed onto the terminal.
An example format would be the following: "0 0 test string". This would print "test string" at position
0,0 on the terminal, which is 0x20001000 according to Capua's memory mapped devices.
The compiler takes in two arguments: the input file, and the output file.
'''


import sys


def main():

    # argcounter keeps track of how many arguments are passed in. Allows multiple labels to be created.
    argcounter = 1
    # will contain the assembly text to declare a string
    stringargs = []
    # will contain the necessary arguments to print the text onto the terminal
    printargs = []

    # setup to open files, read user input argument, and begin .casm output file
    inputfile = sys.argv[1]
    file = open(inputfile, "r")
    outputfile = open(sys.argv[2], "w")
    outputfile.write(".global start:\n\n" + "start:\nMOV end $S\n")
    reader = file.readlines()
    current_line = 0

    # parses each line and stores relevant info into lists to be assembled into instructions
    for line in reader:

        split_line = line.split(" ", 2)
        current_line += 1
        print(split_line)
        # if the line has fewer than necessary arguments and it's not an empty line, print an error.
        if line[0] != "\n" and len(split_line) < 3:
            print("invalid argument at line " + str(current_line))
            sys.exit(1)

        # if there are enough arguments on the line, parse info and start building. Otherwise, it's an empty line.
        if len(split_line) > 2:

            line_index = 0
            complete_string = ""

            # if the arguments aren't valid integers, or if they go out of bounds (we check string length bounds later)
            if integercheck(split_line[0]) is False or integercheck(split_line[1]) is False:
                print("Invalid x,y coordinates at line " + str(current_line))
                sys.exit(1)

            if 0 > int(split_line[0]) or int(split_line[0]) > 80 or int(split_line[1]) < 0 or int(split_line[1]) > 80:
                print("x,y coordinates out of bounds at line " + str(current_line))
                sys.exit(1)

            # convert arguments into appropriate memory location to print to terminal
            offsetpos = converter(int(split_line[0]), int(split_line[1]))

            # evaluate the rest of the line and assemble the text
            for string_chunks in split_line:
                if line_index > 1:
                    complete_string += str(string_chunks) + " "
                line_index += 1
            complete_string = complete_string[:-2]
            # tuple stores position to print string, length of string, and string itself
            pos_length_tuple = (str(offsetpos), str(len(complete_string)), complete_string)
            print(pos_length_tuple[1])
            printargs.append(pos_length_tuple)

            # now we can assemble the dataAlpha symbol to be added to the end of the assembly file
            text = "text" + str(argcounter) + ":\n.dataAlpha " + complete_string
            stringargs.append(text)
            argcounter += 1

    # reset argcounter to assemble instructions and keep labels unique
    argcounter = 1

    # here we assemble the print loops in the .casm file based on string position and length
    for text in printargs:
        if checkStringBounds(text[0], text[1]):
            outputfile.write("MOV text" + str(argcounter) + " $A\n" +
                             "MOV #" + text[0] + " $B\n" +
                             "MOV #" + text[1] + " $C\n" +
                             "print_loop" + str(argcounter) + ":\n" +
                             "MEMR [1] $A $D\n" +
                             "MEMW [1] $D $B\n" +
                             "ADD #1 $A\n" +
                             "ADD #1 $B\n" +
                             "SUB #1 $C\n" +
                             "CMP #0 $C\n" +
                             "JMP <LH> print_loop" + str(argcounter) + "\n\n")
        else:
            print("Some values may have ended out of bounds, and will thus not be printed to the terminal.")
        argcounter += 1

    # Add this to the end of runnable code to prevent crash
    outputfile.write("EndlessLoop:\n"
                     "JMP <> EndlessLoop\n")

    # Append string symbols at the end of the file so they don't interfere with the rest of the code
    for text in stringargs:
        outputfile.write(text + "\n")

    outputfile.write("\nend:\n")
    outputfile.close()
    file.close()


# converts the x,y coordinates in code file to capua terminal's appropriate memory location
def converter(num, num2):

    origin = 536875008
    num = num*80  # y coordinate is printed every 80 chars
    origin = origin + num + num2
    return origin


# check if the values passed in are actual integers
def integercheck(num):

    try:
        int(num)
        return True
    except ValueError:
        return False


# calculates whether the string will print out of bounds and returns boolean value
def checkStringBounds(arg1, arg2):

    maxpos = 536875008 + 2000
    if int(arg1) + int(arg2) > maxpos:
        return False
    return True


if __name__ == '__main__':
    main()
