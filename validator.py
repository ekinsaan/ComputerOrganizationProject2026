from lookup import R_TYPE, I_TYPE, S_TYPE, B_TYPE, U_TYPE, J_TYPE, REGISTERS

def validate(parsed_output):
    all_types = {
        "R": R_TYPE,
        "I": I_TYPE, 
        "S": S_TYPE,
        "B": B_TYPE, 
        "U": U_TYPE, 
        "J": J_TYPE
    }
    all_ops = {}
    for i, j in all_types.items():
        for op in j:
            all_ops[op] = i

    immediate_range = {
        "I": (-2048,2047),
        "S": (-2048,2047),
        "B": (-4096,4095),  
        "J": (-1048576,1048575),  
        "U": (0,1048575),  
    }

    no_of_operands = {
        "R": 3,
        "I": 3,
        "S": 3,
        "B": 3,
        "U": 2,
        "J": 2
    }

    def find_immediate(operands):
        for op in operands:
            if type(op) == int:
                return op
            elif op.lstrip("-").isdigit():
                return int(op)
        return None
    
    errors = []
    for pc, instructions in parsed_output.items():
        instruction_type = instructions[0]
        opcode   = instructions[1]
        operands = instructions[2:]

        # unknown instruction
        if opcode not in all_ops: 
            errors.append(f"PC {pc}: unknown instruction")
            continue
            
        #Check if the instruction has the correct number of operands
        if instruction_type in no_of_operands:
            expected_count = no_of_operands[instruction_type]
            if len(operands) != expected_count:
                errors.append(f"PC {pc}: doesnt have the expected no. of operands")
                continue

        # check if immediates are in hexadecimal
        hex_found = False
        for op in operands:
            if type(op) == str and op.lstrip("-").startswith(("0x", "0X")):  
                errors.append(f"PC {pc}: has a hexadecimal immediate. Only decimal values are accepted")
                hex_found = True
        if hex_found:
            continue    

        # checking registers
        for op in operands:
            if type(op) == int or op.lstrip("-").isdigit():
                continue
            if op not in REGISTERS:
                errors.append(f"PC {pc}: has a invalid register")
                
        # check if immediate is in range
        if instruction_type in immediate_range:
            low, high = immediate_range[instruction_type]
            imm = find_immediate(operands)
            if imm is None:
                errors.append(f"PC {pc}: doesnt have an immediate value")
            elif imm < low or imm > high:
                errors.append(f"PC {pc}: immediate is out of range") 

    #check for virtual halt
    last_pc = len(parsed_output) - 1
    last_instr = parsed_output[last_pc]
    opcode   = last_instr[1]
    operands = last_instr[2:]
    if not (opcode == "beq" and operands[0] == "zero" and operands[1] == "zero" and operands[2] == "0") :
        errors.append("missing halt instruction at end of program")

    if errors: 
        for i in errors: 
            print(i)
        return False
    else:
        return True 
