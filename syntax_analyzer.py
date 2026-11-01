"""Recursive-descent parser that builds a parse tree and a simplified AST."""

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t["type"] != "EOF"]
        self.pos = 0
        self.trace = []

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else {"type":"EOF", "lexeme":"EOF", "line":1}

    def eat(self, lexeme=None, typ=None):
        tok = self.current()
        if lexeme is not None and tok["lexeme"] != lexeme:
            raise ParseError(f"Line {tok.get('line', 1)}: expected {lexeme!r}, found {tok['lexeme']!r}.")
        if typ is not None and tok["type"] != typ:
            raise ParseError(f"Line {tok.get('line', 1)}: expected {typ}, found {tok['lexeme']!r}.")
        self.pos += 1
        self.trace.append(f"Matched {tok['lexeme']!r} ({tok['type']})")
        return tok

    def parse(self):
        children, body = [], []
        while self.pos < len(self.tokens):
            node, tree = self.statement()
            body.append(node); children.append(tree)
        return {"type":"Program", "body":body}, {"name":"Program", "children":children}

    def statement(self):
        tok = self.current(); value = tok["lexeme"]
        if value in ("int", "float", "char", "bool"):
            typ = self.eat()["lexeme"]; names=[]; name=self.eat(typ="ID"); names.append(name["lexeme"])
            while self.current()["lexeme"] == ",":
                self.eat(","); names.append(self.eat(typ="ID")["lexeme"])
            self.eat(";")
            node={"type":"Declaration", "var_type":typ, "names":names, "line":tok.get("line",1)}
            return node, {"name":"Declaration", "children":[{"name":typ}, *[{"name":n} for n in names], {"name":";"}]}
        if value == "print":
            self.eat("print"); self.eat("("); expr, tree=self.expression(); self.eat(")"); self.eat(";")
            return {"type":"Print", "expr":expr, "line":tok.get("line",1)}, {"name":"Print", "children":[{"name":"print"},{"name":"("},tree,{"name":")"},{"name":";"}]}
        if value == "if":
            self.eat("if"); self.eat("("); cond, ct=self.expression(); self.eat(")"); then, tt=self.block(); otherwise=None; children=[{"name":"if"},{"name":"("},ct,{"name":")"},tt]
            if self.current()["lexeme"] == "else":
                self.eat("else"); otherwise, ot=self.block(); children.extend([{"name":"else"},ot])
            return {"type":"If", "condition":cond, "then":then, "else":otherwise, "line":tok.get("line",1)}, {"name":"IfStatement", "children":children}
        if value == "while":
            self.eat("while"); self.eat("("); cond, ct=self.expression(); self.eat(")"); body, bt=self.block()
            return {"type":"While", "condition":cond, "body":body, "line":tok.get("line",1)}, {"name":"WhileStatement", "children":[{"name":"while"},{"name":"("},ct,{"name":")"},bt]}
        if value == "{":
            body, tree=self.block()
            return {"type":"Block", "body":body, "line":tok.get("line",1)}, tree
        name=self.eat(typ="ID"); self.eat("="); expr, et=self.expression(); self.eat(";")
        return {"type":"Assignment", "name":name["lexeme"], "expr":expr, "line":name.get("line",1)}, {"name":"Assignment", "children":[{"name":name["lexeme"]},{"name":"="},et,{"name":";"}]}

    def block(self):
        self.eat("{"); body=[]; children=[]
        while self.current()["lexeme"] != "}" and self.pos < len(self.tokens):
            node, tree=self.statement(); body.append(node); children.append(tree)
        self.eat("}")
        return body, {"name":"Block", "children":[{"name":"{"},*children,{"name":"}"}]}

    def expression(self): return self.comparison()
    def comparison(self):
        node, tree=self.additive()
        while self.current()["lexeme"] in ("==","!=","<",">","<=",">="):
            op=self.eat()["lexeme"]; right, rt=self.additive(); node={"type":"Binary", "op":op, "left":node, "right":right}; tree={"name":op,"children":[tree,rt]}
        return node, tree
    def additive(self):
        node, tree=self.term()
        while self.current()["lexeme"] in ("+","-"):
            op=self.eat()["lexeme"]; right, rt=self.term(); node={"type":"Binary","op":op,"left":node,"right":right}; tree={"name":op,"children":[tree,rt]}
        return node, tree
    def term(self):
        node, tree=self.factor()
        while self.current()["lexeme"] in ("*","/","%"):
            op=self.eat()["lexeme"]; right, rt=self.factor(); node={"type":"Binary","op":op,"left":node,"right":right}; tree={"name":op,"children":[tree,rt]}
        return node, tree
    def factor(self):
        tok=self.current()
        if tok["lexeme"] == "(":
            self.eat("("); node, tree=self.expression(); self.eat(")"); return node, {"name":"Parenthesized","children":[{"name":"("},tree,{"name":")"}]}
        if tok["type"] == "NUMBER":
            self.eat(); return {"type":"Number","value":tok["lexeme"]}, {"name":tok["lexeme"]}
        if tok["type"] == "ID":
            self.eat(); return {"type":"Identifier","name":tok["lexeme"]}, {"name":tok["lexeme"]}
        raise ParseError(f"Line {tok.get('line',1)}: unexpected token {tok['lexeme']!r} in expression.")


def parse_tokens(tokens):
    parser=Parser(tokens)
    ast, tree=parser.parse()
    return ast, tree, parser.trace, []
