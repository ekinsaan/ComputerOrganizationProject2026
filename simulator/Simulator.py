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
