"""Translate TAC into readable pseudo-assembly."""

def generate_target_code(code):
    out=[]
    for line in code:
        if line.startswith("label "):
            out.append(line.split()[1]+":")
        elif line.startswith("goto "):
            out.append("JMP "+line.split()[1])
        elif line.startswith("ifFalse "):
            parts=line.split(); out.append(f"JZ {parts[1]} {parts[3]}")
        elif line.startswith("print "):
            out.append("PRINT "+line[6:])
        elif " = " in line:
            dest,rhs=line.split(" = ",1); parts=rhs.split()
            if len(parts)==3:
                a,op,b=parts; out.extend([f"LOAD R1, {a}",f"{ {'+':'ADD','-':'SUB','*':'MUL','/':'DIV','%':'MOD','>':'CMPGT','<':'CMPLT','>=':'CMPGE','<=':'CMPLE','==':'CMPEQ','!=':'CMPNE'}.get(op,'OP')} R1, {b}",f"STORE {dest}, R1"])
            else: out.extend([f"LOAD R1, {rhs}",f"STORE {dest}, R1"])
    return out
