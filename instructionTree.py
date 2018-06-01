#!/usr/bin/env python

from InstructionForms import STATE0, \
                             STATE1, \
                             STATE2, \
                             STATE3, \
                             STATE4, \
                             STATE5, \
                             STATE6, \
                             STATE7, \
                             STATE8, \
                             STATE9, \
                             STATE10, \
                             INSTRUCTION_LIST, \
                             INDICATOR_LIST

from Configuration import REGISTER_A, \
                          REGISTER_B, \
                          REGISTER_C, \
                          REGISTER_D, \
                          REGISTER_E, \
                          REGISTER_F, \
                          REGISTER_G, \
                          REGISTER_A2, \
                          REGISTER_B2, \
                          REGISTER_C2, \
                          REGISTER_D2, \
                          REGISTER_E2, \
                          REGISTER_F2, \
                          REGISTER_G2, \
                          REGISTER_S, \
                          REGISTER_S2


class InstructionTree:

    relativeAddressCounter = 0

    def build(self, text):
        line = text.split()
        instruction = b""
        offset = 0
        arglist = []
        found = False
        form = "INS"
        labelFlag = 0
        data_identifier = line[0]  # used for special identifiers such as .dataAlpha, comments etc.

        # first off, we need to determine if this line has a label or global label to be referenced
        if data_identifier[-1] == ":":
            label = data_identifier[:-1]
            return label, self.relativeAddressCounter, 1

        elif data_identifier == ".GLOBAL":
            label = line[1]
            return label, self.relativeAddressCounter, 2

        elif data_identifier[0] == ";":
            return "", "", 3

        elif line[0] == ".DATAALPHA":
            text = text.split(maxsplit=1)
            instruction += text.encode("utf-8")
            self.relativeAddressCounter += len(instruction) + 1
            instruction += b"\x00"
            return instruction, self.relativeAddressCounter, 0

        elif line[0] == ".DATANUMERIC":
            instruction += str(line[1])
            self.relativeAddressCounter += 4
            return instruction, self.relativeAddressCounter, 0

        elif line[0] == ".DATAMEMREF":
            instruction += str(line[1])
            self.relativeAddressCounter += 4
            return instruction, self.relativeAddressCounter, 0

        # Next we check if the first item on the line is an instruction
        elif line[0] in INSTRUCTION_LIST:
            labelFlag = 0

            for arg in line[1:]:
                if arg[0] == "$":
                    form += "REG"
                elif arg[0] == "#":
                    form += "IMM"
                elif arg[0] == "<" and arg[-1] == ">":
                    form += "FLAG"
                elif arg[0] == "[" and arg[-1] == "]":
                    form += "WIDTH"
                else:
                    form += "IMM"

                arglist.append(arg)

            state = self._definestate(form)

            for ins in state:

                if line[0] == ins[0]:
                    instruction += bytes((ins[1],))
                    self.relativeAddressCounter += ins[2]
                    found = True

            if not found:
                raise ValueError("Invalid instruction format")  # theoretically this shouldn't happen

            if state == STATE0:
                # Instruction is already complete
                pass

            elif state == STATE1:
                register = self.translateRegisterNameToRegisterCode(arglist[0][1:])
                instruction += bytes(0b0000) + bytes((register,))

            elif state == STATE2:
                register = self.translateRegisterNameToRegisterCode(arglist[0][1:])
                register2 = self.translateRegisterNameToRegisterCode(arglist[1][1:])
                register = (register << 4) + register2
                instruction += bytes((register,))

            elif state == STATE3:
                immediate = self.translateTextImmediateToImmediate(arglist[0][1:])
                instruction += bytes((immediate,))

            elif state == STATE4:
                immediate = self.translateTextImmediateToImmediate(arglist[0][1:])
                register = self.translateRegisterNameToRegisterCode(arglist[1][1:])
                instruction += bytes((immediate,)) + bytes(0b0000) + bytes((register,))

            elif state == STATE5:
                width = arglist[0][1:-1]
                immediate = self.translateTextImmediateToImmediate(arglist[1][1:])
                immediate2 = self.translateTextImmediateToImmediate(arglist[2][1:])
                instruction += bytes(0b0000) + bytes((width,)) + bytes((immediate,)) + bytes((immediate2,))

            elif state == STATE6:
                width = arglist[0][1:-1]
                immediate = self.translateTextImmediateToImmediate(arglist[1][1:])
                register = self.translateRegisterNameToRegisterCode(arglist[2][1:])
                instruction += bytes((width,)) + bytes((register,)) + bytes((immediate,))

            elif state == STATE7:
                width = arglist[0][1:-1]
                register = self.translateRegisterNameToRegisterCode(arglist[1][1:])
                register2 = self.translateRegisterNameToRegisterCode(arglist[2][1:])
                instruction += bytes((width,)) + bytes((register,)) + bytes(0b0000) + bytes((register2,))

            elif state == STATE8:
                pass

            elif state == STATE9:
                pass

            elif state == STATE10:
                pass

        else:
            # Nothing was valid in the first argument
            raise ValueError("Invalid instruction format")

        return instruction, self.relativeAddressCounter, labelFlag

    def translateRegisterNameToRegisterCode(self, registerName: str=""):
        """
        This takes a register name and returns a register code as per:
            A = 0b00
            B = 0b01
            C = 0b10
            ...
            S = 0b111
        Throws error if register is not A-G, or S
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
        elif registerName == "S":
            registerCode = REGISTER_S
        else:
            raise ValueError("Invalid register provided. '{}' seen as input, expect A, B, C or S.".format(registerName))

        return registerCode

    def translateTextImmediateToImmediate(self, textImmediate: str=""):
        """
        This will translate an immediate value in a way that can be understood by the architecture.
        :param textImmediate: str, an immediate value to be translated
        :return: int, an immediate that can be worked on
        """
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

    def translateTextFlagsToCodeFlags(self, textFlags):
        """
        Will translate a text FLAGs to flags code as:
        FLAGS: 0b000 : Zero, Lower, Higher
        :param textFlags:
        :return:
        """
        codeFlags = 0b000
        originalFlags = textFlags
        textFlags = textFlags.lower()

        if "z" in textFlags or "e" in textFlags:
            codeFlags |= 0b100
            textFlags = textFlags.replace("z", "")
            textFlags = textFlags.replace("e", "")

        if "l" in textFlags:
            codeFlags |= 0b010
            textFlags = textFlags.replace("l", "")

        if "h" in textFlags:
            codeFlags |= 0b001
            textFlags = textFlags.replace("h", "")

        if len(textFlags) > 0:
            # Invalid flag selection detected!
            raise ValueError("Invalid conditional flag detected {} was provided but is invalid".format(originalFlags))

        return codeFlags

    def _definestate(self, form):
        if form == "INS":
            form = STATE0
            return form
        elif form == "INSREG":
            form = STATE1
            return form
        elif form == "INSREGREG":
            form = STATE2
            return form
        elif form == "INSIMM":
            form = STATE3
            return form
        elif form == "INSIMMREG":
            form = STATE4
            return form
        elif form == "INSWIDTHIMMIMM":
            form = STATE5
            return form
        elif form == "INSWIDTHIMMREG":
            form = STATE6
            return form
        elif form == "INSWIDTHREGIMM":
            form = STATE7
            return form
        elif form == "INSWIDTHREGREG":
            form = STATE8
            return form
        elif form == "INSFLAGIMM":
            form = STATE9
            return form
        elif form == "INSFLAGREG":
            form = STATE10
            return form
        else:
            # too many arguments or arguments don't fit any description
            raise ValueError("Invalid instruction format")
