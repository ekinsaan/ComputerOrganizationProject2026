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
    return 0

def MemoryWrite(address, value):
    if 0x00010000 <= address <= 0x0001007F:
        DataMemory[(address - 0x00010000) // 4] = value & 0xFFFFFFFF
    elif 0x00000100 <= address <= 0x0000017F:
        StackMemory[(address - 0x00000100) // 4] = value & 0xFFFFFFFF

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
