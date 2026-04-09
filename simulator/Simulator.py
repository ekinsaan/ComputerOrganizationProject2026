import sys
import lookup

Registers = [0] * 32
ProgramCounter = 0
Instructions = []
DataMemory = [0] * 32
StackMemory = [0] * 32

Registers[2] = 0x0000017C

OutputLines = []

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

def Execute(decoded):
    if decoded["type"] == "R":
        Execute_R_Type(decoded)
