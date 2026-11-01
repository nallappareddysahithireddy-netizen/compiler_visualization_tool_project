"""Symbol table helpers."""


def build_symbol_table(ast):
    symbols, errors, warnings = [], [], []
    by_name = {}

    def declare(name, typ, line=1):
        if name in by_name:
            errors.append(f"Line {line}: duplicate declaration of '{name}'.")
            return
        entry = {"name": name, "type": typ, "scope": "global", "initialized": False, "line": line}
        by_name[name] = entry
        symbols.append(entry)

    def visit(node):
        if not isinstance(node, dict):
            return
        kind = node.get("type")
        if kind == "Declaration":
            for name in node.get("names", []):
                declare(name, node.get("var_type", "int"), node.get("line", 1))
        for key, value in node.items():
            if key in ("type", "var_type", "names", "line", "value", "name", "op"):
                continue
            if isinstance(value, dict):
                visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        visit(item)
    visit(ast)
    return symbols, errors, by_name
