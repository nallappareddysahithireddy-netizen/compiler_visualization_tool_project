"""Generate three-address code, quadruples and triples from the AST."""

class TACGenerator:
    def __init__(self): self.code=[]; self.temp=0; self.label=0
    def t(self): self.temp+=1; return f"t{self.temp}"
    def l(self): self.label+=1; return f"L{self.label}"
    def expr(self,node):
        kind=node.get("type")
        if kind in ("Number","Identifier"): return node.get("value",node.get("name"))
        if kind=="Binary":
            left=self.expr(node["left"]); right=self.expr(node["right"]); temp=self.t(); self.code.append(f"{temp} = {left} {node['op']} {right}"); return temp
        return "?"
    def statements(self,nodes):
        for node in nodes:
            kind=node.get("type")
            if kind=="Declaration": continue
            if kind=="Assignment": self.code.append(f"{node['name']} = {self.expr(node['expr'])}")
            elif kind=="Print": self.code.append(f"print {self.expr(node['expr'])}")
            elif kind=="Block": self.statements(node.get("body",[]))
            elif kind=="If":
                else_label=self.l(); end_label=self.l(); cond=self.expr(node["condition"]); self.code.append(f"ifFalse {cond} goto {else_label}"); self.statements(node.get("then",[]))
                if node.get("else") is not None: self.code.append(f"goto {end_label}")
                self.code.append(f"label {else_label}")
                if node.get("else") is not None: self.statements(node["else"]); self.code.append(f"label {end_label}")
            elif kind=="While":
                start=self.l(); end=self.l(); self.code.append(f"label {start}"); cond=self.expr(node["condition"]); self.code.append(f"ifFalse {cond} goto {end}"); self.statements(node.get("body",[])); self.code.append(f"goto {start}"); self.code.append(f"label {end}")
    def generate(self,ast): self.statements(ast.get("body",[])); return self.code


def make_quadruples(code):
    result=[]
    for i,line in enumerate(code,1):
        if line.startswith("label ") or line.startswith("goto ") or line.startswith("ifFalse ") or line.startswith("print "):
            parts=line.split(); result.append({"index":i,"operator":parts[0],"arg1":" ".join(parts[1:]),"arg2":"","result":""})
        elif " = " in line:
            dest,rhs=line.split(" = ",1); parts=rhs.split()
            if len(parts)==3: op,a,b=parts; result.append({"index":i,"operator":op,"arg1":a,"arg2":b,"result":dest})
            else: result.append({"index":i,"operator":"=","arg1":rhs,"arg2":"","result":dest})
    return result


def make_triples(quads):
    return [{"index":q["index"],"operator":q["operator"],"arg1":q["arg1"],"arg2":q["arg2"]} for q in quads]
