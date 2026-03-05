from lookup import R_TYPE, I_TYPE, S_TYPE, B_TYPE, U_TYPE, J_TYPE, REGISTERS

# Functions used in Parser

def GetOpType(Op):
    if Op in R_TYPE:
        return "R"
    if Op in I_TYPE:
        return "I"
    if Op in S_TYPE:
        return "S"
    if Op in B_TYPE:
        return "B"
    if Op in U_TYPE:
        return "U"
    if Op in J_TYPE:
        return "J"
    return None

def ParseLine(Line):
    # strip commas
    Line = Line.strip()
    Line = Line.replace(",", " ")

    Line = Line.split()
    Elements = Line

    for i in Elements:
        if "(" in i:
            index = Line.index(i)
            Line.remove(i)
            parts = i.split("(")
            parts[1] = parts[1][:-1] # removing )
            Line.insert(index,parts[1])
            Line.insert(index,parts[0])

    return Line

def Parse(FilePath):
    with open(FilePath, "r") as f:
        # ignores empty lines, this line below has been created using online sources
        RawLines = f.readlines()

        output = {}
        labels = {}

        pc = 0

        for i in RawLines:
            if not i or i == "\n":
                pc += 1
                continue

            i = ParseLine(i)

            if i[0][-1] == ":":
                i[0] = i[0][:-1]
                labels[i[0]] = pc
                i.pop(0)

            if not i or i == "\n":
                pc += 1
                continue

            i.insert(0,GetOpType(i[0]))

            output[pc] = i

            pc += 1

        for i, j in output.items():
            for k in output[i]:
                for l in labels.keys():
                    if k == l:
                        output[i][output[i].index(k)] = labels[l] - i

        return output

test = r"C:\Users\HP\CollegeProjects\CO_Sem2_Project\test.txt"
testparse = Parse(test)

for i,j in testparse.items():
    print(i+1,j)