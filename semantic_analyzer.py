"""Basic semantic checks for declaration and expression use."""

def analyze_semantics(ast, symbols):
    table={s["name"]:s for s in symbols}; errors=[]; warnings=[]
    def expr(node, line=1):
        if not isinstance(node, dict): return
        if node.get("type")=="Identifier":
            name=node["name"]
            if name not in table: errors.append(f"Line {line}: identifier '{name}' is used before declaration.")
            else: table[name]["initialized"] = True
        elif node.get("type")=="Binary": expr(node.get("left"),line); expr(node.get("right"),line)
    def walk(node):
        if isinstance(node,list):
            for n in node: walk(n)
            return
        if not isinstance(node,dict): return
        kind=node.get("type"); line=node.get("line",1)
        if kind=="Assignment":
            if node["name"] not in table: errors.append(f"Line {line}: assignment to undeclared identifier '{node['name']}'.")
            expr(node.get("expr"),line)
            if node["name"] in table: table[node["name"]]["initialized"] = True
        elif kind=="Declaration": pass
        elif kind=="Print": expr(node.get("expr"),line)
        elif kind=="If": expr(node.get("condition"),line); walk(node.get("then",[])); walk(node.get("else",[]))
        elif kind=="While": expr(node.get("condition"),line); walk(node.get("body",[]))
        elif kind in ("Program","Block"): walk(node.get("body",[]))
    walk(ast)
    return errors, warnings, symbols
