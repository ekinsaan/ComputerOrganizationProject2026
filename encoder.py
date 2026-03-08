from lookup import R_TYPE, R_TYPE_OPCODE, I_TYPE, S_TYPE, S_TYPE_OPCODE, B_TYPE, B_TYPE_OPCODE, U_TYPE, J_TYPE, REGISTERS

def imm_to_binary(value,no_of_bits):
    value = int(value)
    if value < 0:
        value = (1 << no_of_bits) + value   #if value is negative we convert ,then the MSB must be 1
    #using built-in function format to convert an integer into binary
    return format(value,f'0{no_of_bits}b')

def encode_instruction(parsed_dict):
    code = []           #parsed_dict is output from parse

    for pc,instruction in parsed_dict.items():
        op_type = instruction[0]
        op = instruction[1]

        try:
            if op_type == "R": 
                #Format: funct7(7) rs2(5) rs1(5) funct3(3) rd(5) opcode(7)
                funct7,funct3 = R_TYPE[op]
                rd = REGISTERS[instruction[2]]
                rs1 = REGISTERS[instruction[3]]
                rs2 = REGISTERS[instruction[4]]

                binary_instruction = funct7 + rs2 + rs1 + funct3 + rd + R_TYPE_OPCODE

            elif op_type == "I": 
                #Format: imm(12) rs1(5) funct3(3) rd(5) opcode(7)
                opcode,funct3 = I_TYPE[op]
                if op == "lw": 
                    #lw is formatted as [type,op,rd,imm,rs1]
                    rd = REGISTERS[instruction[2]]
                    imm = imm_to_binary(instruction[3],12)
                    rs1 = REGISTERS[instruction[4]]
                else: 
                    #other I-types are formatted as [type,op,rd,rs1,imm]
                    rd = REGISTERS[instruction[2]]
                    rs1 = REGISTERS[instruction[3]]
                    imm = imm_to_binary(instruction[4],12)
                
                binary_instruction = imm + rs1 + funct3 + rd + opcode

            elif op_type == "S":
                #Format: imm[11 : 5](7) rs2(5) rs1(5) funct3(3) imm[4 : 0](5) opcode(7)
                rs2 = REGISTERS[instruction[2]]
                imm = imm_to_binary(instruction[3],12)
                rs1 = REGISTERS[instruction[4]]
                funct3 = S_TYPE[op]

                binary_instruction = imm[0:7] + rs2 + rs1 + funct3 + imm[7:12] + S_TYPE_OPCODE

            elif op_type == "B":
                #Format: imm[12](1) imm[10:5](6) rs2(5) rs1(5) funct3(3) imm[4:1](4) imm[11](1) opcode(7)
                rs1 = REGISTERS[instruction[2]]
                rs2 = REGISTERS[instruction[3]]
                funct3 = B_TYPE[op]

                imm_value = int(instruction[4]) * 4  # multiplying relative instruction offset by 4 for byte addressing
                imm = imm_to_binary(imm_value,13)

                binary_instruction = imm[0] + imm[2:8] + rs2 + rs1 + funct3 + imm[8:12] + imm[1] + B_TYPE_OPCODE

            elif op_type == "U":
                #Format: imm[31:12](20) rd(5) opcode(7)
                rd = REGISTERS[instruction[2]]
                imm_value = int(instruction[3])
                imm = imm_to_binary(imm_value,32)
                opcode = U_TYPE[op]

                binary_instruction = imm[0:20] + rd + opcode

            elif op_type == "J":
                #Format: imm[20](1) imm[10:1](10) imm[11](1) imm[19:12](8) rd(5) opcode(7)
                rd = REGISTERS[instruction[2]]
                opcode = J_TYPE[op]

                imm_value = int(instruction[3]) * 4  # multiplying relative instruction offset by 4 for byte addressing
                imm = imm_to_binary(imm_value,21)

                binary_instruction = imm[0] + imm[10:20] + imm[9] + imm[1:9] + rd + opcode

            code.append((pc , binary_instruction))

        except Exception as error:
            #print(f"Error encoding instruction at PC {pc}: {instruction}. Error: {error}")
            pass


    return code
