"""Lexical analyzer for the educational mini-C language."""
import re

TOKEN_SPEC = [
    ("COMMENT", r"//[^\n]*|/\*[\s\S]*?\*/"),
    ("NUMBER", r"\d+(?:\.\d+)?"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"==|!=|<=|>=|\+\+|--|[+\-*/%=<>!]"),
    ("PUNCT", r"[(){};,]"),
    ("SKIP", r"[ \t\r\n]+"),
    ("MISMATCH", r"."),
]
TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))
KEYWORDS = {"int", "float", "char", "if", "else", "while", "print", "return", "void", "bool"}


def tokenize(source):
    tokens, errors, steps = [], [], []
    for match in TOKEN_RE.finditer(source):
        kind, value = match.lastgroup, match.group()
        line = source.count("\n", 0, match.start()) + 1
        col = match.start() - source.rfind("\n", 0, match.start())
        if kind in ("SKIP", "COMMENT"):
            continue
        if kind == "MISMATCH":
            errors.append(f"Line {line}, column {col}: unexpected character {value!r}")
            continue
        if kind == "ID" and value in KEYWORDS:
            kind = "KEYWORD"
        elif kind == "PUNCT":
            kind = "PUNCTUATION"
        token = {"index": len(tokens) + 1, "type": kind, "lexeme": value, "line": line, "column": col}
        tokens.append(token)
        steps.append({"step": len(steps) + 1, "lexeme": value, "recognized_as": kind, "line": line})
    tokens.append({"index": len(tokens) + 1, "type": "EOF", "lexeme": "EOF", "line": source.count("\n") + 1, "column": 1})
    return {"tokens": tokens, "errors": errors, "steps": steps}
