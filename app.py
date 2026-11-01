
from flask import Flask, render_template, request, jsonify

from lexer import tokenize
from syntax_analyzer import parse_tokens, ParseError
from symbol_table import build_symbol_table
from semantic_analyzer import analyze_semantics
from intermediate_code import (
    TACGenerator,
    make_quadruples,
    make_triples,
)
from control_flow import build_control_flow
from optimizer import optimize_code
from target_code import generate_target_code

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/compile")
def compile_source():
    payload = request.get_json(silent=True) or request.form
    source = payload.get("source", "")

    result = {
        "source": source,
        "tokens": [],
        "scanner_steps": [],
        "lexical_errors": [],
        "ast": None,
        "parse_tree": None,
        "parser_trace": [],
        "syntax_errors": [],
        "symbols": [],
        "semantic_errors": [],
        "semantic_warnings": [],
        "tac": [],
        "quadruples": [],
        "triples": [],
        "basic_blocks": [],
        "cfg": {"nodes": [], "edges": []},
        "optimized_tac": [],
        "optimization_log": [],
        "target_code": [],
    }

    try:
        # 1. Lexical analysis
        lex = tokenize(source)

        result.update(
            tokens=lex.get("tokens", []),
            scanner_steps=lex.get("steps", []),
            lexical_errors=lex.get("errors", []),
        )

        if result["lexical_errors"]:
            return jsonify(result)

        # 2. Syntax analysis
        try:
            ast, tree, trace, errors = parse_tokens(
                result["tokens"]
            )

            result.update(
                ast=ast,
                parse_tree=tree,
                parser_trace=trace,
                syntax_errors=errors,
            )

        except ParseError as exc:
            result["syntax_errors"] = [str(exc)]
            return jsonify(result)

        if result["syntax_errors"]:
            return jsonify(result)

        # 3. Symbol table and semantic analysis
        symbols, declaration_errors, _ = build_symbol_table(ast)

        semantic_errors, warnings, symbols = analyze_semantics(
            ast, symbols
        )

        result.update(
            symbols=symbols,
            semantic_errors=declaration_errors + semantic_errors,
            semantic_warnings=warnings,
        )

        if result["semantic_errors"]:
            return jsonify(result)

        # 4. Intermediate code generation
        generator = TACGenerator()
        tac = generator.generate(ast)

        quadruples = make_quadruples(tac)
        triples = make_triples(quadruples)

        # 5. Control-flow analysis
        basic_blocks, cfg = build_control_flow(tac)

        # 6. Code optimization
        _before, optimized_tac, optimization_log = optimize_code(tac)

        # 7. Target code generation
        target_code = generate_target_code(optimized_tac)

        result.update(
            tac=tac,
            quadruples=quadruples,
            triples=triples,
            basic_blocks=basic_blocks,
            cfg=cfg,
            optimized_tac=optimized_tac,
            optimization_log=optimization_log,
            target_code=target_code,
        )

    except Exception as exc:
        app.logger.exception("Compilation failed")
        result["semantic_errors"].append(
            f"Internal compiler error: {type(exc).__name__}: {exc}"
        )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
