"""Small, educational local optimizations for TAC."""
import re

def optimize_code(code):
    before=list(code); after=[]; log=[]
    for line in code:
        new=line
        m=re.match(r"^(\w+) = (-?\d+(?:\.\d+)?) ([+*\-/]) (-?\d+(?:\.\d+)?)$",line)
        if m:
            dest,a,op,b=m.groups()
            try:
                x,y=float(a),float(b)
                if op=="+": value=x+y
                elif op=="-": value=x-y
                elif op=="*": value=x*y
                elif op=="/" and y!=0: value=x/y
                else: value=None
                if value is not None:
                    value=int(value) if value.is_integer() else value
                    new=f"{dest} = {value}"; log.append(f"Constant folding: {line} → {new}")
            except ValueError: pass
        if new==line:
            m=re.match(r"^(\w+) = (\w+) ([+*]) 0$",line)
            if m and m.group(3)=="+": new=f"{m.group(1)} = {m.group(2)}"
            m=re.match(r"^(\w+) = (\w+) \* 1$",line)
            if m: new=f"{m.group(1)} = {m.group(2)}"
            if new!=line: log.append(f"Algebraic simplification: {line} → {new}")
        after.append(new)
    return before,after,log
