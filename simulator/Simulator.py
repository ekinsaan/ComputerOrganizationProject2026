import sys
import lookup

Registers = [0] * 32
ProgramCounter = 0
Instructions = []
DataMemory = [0] * 32
StackMemory = [0] * 32

Registers[2] = 0x0000017C

OutputLines = []

def DecimalToSignedBinary(number):
    return f"{number & ((1 << 32) - 1):0{32}b}"

def SignedBinaryToDecimal(number):
    if number[0] == '1':
        return int(number, 2) - (1 << len(number))
    else:
        return int(number, 2)

def MemoryRead(address):
    if 0x00010000 <= address <= 0x0001007F:
        return DataMemory[(address - 0x00010000) // 4]
    elif 0x00000100 <= address <= 0x0000017F:
        return StackMemory[(address - 0x00000100) // 4]
    else:
        print(f"Invalid memory acess at 0x{address:08X}")
        with open(OutputPath, "w") as f:
            for i in OutputLines:
                f.write(i + "\n")
        sys.exit(1)

def MemoryWrite(address, value):

    if address % 4 != 0:
        print(f"Unaligned memory access at 0x{address:08X}")
        with open(OutputPath, "w") as f:
            for i in OutputLines:
                f.write(i + "\n")
        sys.exit(1)

    if 0x00010000 <= address <= 0x0001007F:
        DataMemory[(address - 0x00010000) // 4] = value & 0xFFFFFFFF
    elif 0x00000100 <= address <= 0x0000017F:
        StackMemory[(address - 0x00000100) // 4] = value & 0xFFFFFFFF
    else:
        print(f"Invalid memory acess at 0x{address:08X}")
        with open(OutputPath, "w") as f:
            for i in OutputLines:
                f.write(i + "\n")
        sys.exit(1)

def GetLine():
    return Instructions[ProgramCounter // 4]

def Decode(line):
    decoded = {}

    opcode = line[-7:]
    instructiontype = lookup.OPCODES[opcode]

    decoded["opcode"] = opcode
    decoded["type"] = instructiontype

    if instructiontype == "R":
        decoded["rd"] = int(line[-12:-7],2)
        decoded["funct3"] = line[-15:-12]
        decoded["rs1"] = int(line[-20:-15],2)
        decoded["rs2"] = int(line[-25:-20],2)
        decoded["funct7"] = line[:-25]

    return decoded

def Execute_R_Type(Decoded):
    global ProgramCounter
    rs1 = Registers[Decoded["rs1"]]
    rs2 = Registers[Decoded["rs2"]]
    rd = Decoded["rd"]

    if Decoded["funct3"] == "000":
        if Decoded["funct7"] == "0000000":
            #add
            Registers[rd] = (rs1 + rs2) & 0xFFFFFFFF
            ProgramCounter += 4
            
        elif Decoded["funct7"] == "0100000":
            #sub
            Registers[rd] = (rs1 - rs2) & 0xFFFFFFFF
            ProgramCounter += 4

    elif Decoded["funct3"] == "001":
        if Decoded["funct7"] == "0000000":
            #sll
            shamt = rs2 & 0x1F
            Registers[rd] = (rs1 << shamt) & 0xFFFFFFFF
            ProgramCounter += 4

    elif Decoded["funct3"] == "010":
        if Decoded["funct7"] == "0000000":
            #slt
            signed_rs1 = rs1 if rs1 < 0x80000000 else rs1 - 0x100000000
            signed_rs2 = rs2 if rs2 < 0x80000000 else rs2 - 0x100000000
            Registers[rd] = 1 if signed_rs1 < signed_rs2 else 0
            ProgramCounter += 4

    elif Decoded["funct3"] == "011":
        if Decoded["funct7"] == "0000000":
            #sltu
            Registers[rd] = 1 if rs1 < rs2 else 0
            ProgramCounter += 4

    elif Decoded["funct3"] == "100":
        if Decoded["funct7"] == "0000000":
            #xor
            Registers[rd] = (rs1 ^ rs2) & 0xFFFFFFFF
            ProgramCounter += 4

    elif Decoded["funct3"] == "101":
        if Decoded["funct7"] == "0000000":
            #srl
            shamt = rs2 & 0x1F
            Registers[rd] = (rs1 & 0xFFFFFFFF) >> shamt
            ProgramCounter += 4

    elif Decoded["funct3"] == "110":
        if Decoded["funct7"] == "0000000":
            #or
            Registers[rd] = (rs1 | rs2) & 0xFFFFFFFF
            ProgramCounter += 4

    elif Decoded["funct3"] == "111":
        if Decoded["funct7"] == "0000000":
            #and
            Registers[rd] = (rs1 & rs2) & 0xFFFFFFFF
            ProgramCounter += 4

def Execute_I_Type(Decoded):
    global ProgramCounter
    rs1 = Registers[Decoded["rs1"]]
    rd  = Decoded["rd"]
    imm = SignedBinaryToDecimal(Decoded["imm"])

    if Decoded["opcode"] == "0000011":
        if Decoded["funct3"] == "010":
            # lw
            address = (rs1 + imm) & 0xFFFFFFFF
            Registers[rd] = MemoryRead(address)
            ProgramCounter += 4

    elif Decoded["opcode"] == "0010011":
        if Decoded["funct3"] == "000":
            # addi
            Registers[rd] = (rs1 + imm) & 0xFFFFFFFF
            ProgramCounter += 4

        elif Decoded["funct3"] == "011":
            # sltiu
            unsigned_rs1 = rs1 & 0xFFFFFFFF
            unsigned_imm = imm & 0xFFFFFFFF
            Registers[rd] = 1 if unsigned_rs1 < unsigned_imm else 0
            ProgramCounter += 4

    elif Decoded["opcode"] == "1100111":
        if Decoded["funct3"] == "000":
            # jalr
            return_address = (ProgramCounter + 4) & 0xFFFFFFFF
            target = (rs1 + imm) & 0xFFFFFFFE
            Registers[rd] = return_address
            ProgramCounter = target

def Execute_S_Type(Decoded):
    global ProgramCounter
    rs1 = Registers[Decoded["rs1"]]
    rs2 = Registers[Decoded["rs2"]]
    imm = SignedBinaryToDecimal(Decoded["imm"])

    if Decoded["funct3"] == "010":
        # sw
        address = (rs1 + imm) & 0xFFFFFFFF
        MemoryWrite(address, rs2)
    ProgramCounter += 4

def Execute_B_Type(Decoded):
    global ProgramCounter
    rs1 = Registers[Decoded["rs1"]]
    rs2 = Registers[Decoded["rs2"]]
    imm = SignedBinaryToDecimal(Decoded["imm"])

    signed_rs1 = rs1 if rs1 < 0x80000000 else rs1 - 0x100000000
    signed_rs2 = rs2 if rs2 < 0x80000000 else rs2 - 0x100000000

    branch = False

    if Decoded["funct3"] == "000":
        # beq
        branch = (rs1 == rs2)

    elif Decoded["funct3"] == "001":
        # bne
        branch = (rs1 != rs2)

    elif Decoded["funct3"] == "100":
        # blt
        branch = (signed_rs1 < signed_rs2)

    elif Decoded["funct3"] == "101":
        # bge
        branch = (signed_rs1 >= signed_rs2)

    elif Decoded["funct3"] == "110":
        # bltu
        branch = (rs1 < rs2)

    elif Decoded["funct3"] == "111":
        # bgeu
        branch = (rs1 >= rs2)

    if branch:
        ProgramCounter = (ProgramCounter + imm) & 0xFFFFFFFF
    else:
        ProgramCounter += 4

def Execute_U_Type(Decoded):
    global ProgramCounter
    rd  = Decoded["rd"]
    imm = int(Decoded["imm"], 2) << 12

    if Decoded["opcode"] == "0110111":
        # lui
        Registers[rd] = imm & 0xFFFFFFFF
        ProgramCounter += 4

    elif Decoded["opcode"] == "0010111":
        # auipc
        Registers[rd] = (ProgramCounter + imm) & 0xFFFFFFFF
        ProgramCounter += 4

def Execute_J_Type(Decoded):
    global ProgramCounter
    rd  = Decoded["rd"]
    imm = SignedBinaryToDecimal(Decoded["imm"])

    # jal
    Registers[rd]  = (ProgramCounter + 4) & 0xFFFFFFFF
    ProgramCounter = (ProgramCounter + imm) & 0xFFFFFFFF

def Execute(decoded):
    if decoded["type"] == "R":
        Execute_R_Type(decoded)

def VirtualHaltCheck(decoded):
    if decoded["type"] == "B":
        if decoded["funct3"] == "000":
            if Registers[decoded["rs1"]] == 0 and Registers[decoded["rs2"]] == 0 and SignedBinaryToDecimal(decoded["imm"]) == 0:
                return True

def CreateRegisterLineWrite():
    output = f"0b{DecimalToSignedBinary(ProgramCounter)} "
    for i in Registers:
        output += f"0b{DecimalToSignedBinary(i)} "
    OutputLines.append(output)

def CreateDataMemoryWrite():
    Counter = 0x00010000
    for i in DataMemory:
        OutputLines.append(f"0x{Counter:0{8}X}:0b{DecimalToSignedBinary(i)}")
        Counter += 4

def Run():
    infinitystop = 0
    while infinitystop < 1000:
        line = GetLine()
        decoded = Decode(line)
        if VirtualHaltCheck(decoded) == True:
            CreateRegisterLineWrite()
            CreateDataMemoryWrite()
            return
        Execute(decoded)
        Registers[0] = 0
        CreateRegisterLineWrite()
        infinitystop += 1
    print(f"Reached {infinitystop} loops")

InputPath  = sys.argv[1]
OutputPath = sys.argv[2]
ReadablePath = sys.argv[3] if len(sys.argv) > 3 else None

with open(InputPath, "r") as f:
    lines = f.readlines()
    for i in lines:
        Instructions.append(i.rstrip())

Run()

with open(OutputPath, "w") as f:
    for i in OutputLines:
        f.write(i + "\n")
