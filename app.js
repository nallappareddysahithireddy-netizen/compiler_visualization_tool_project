const phases = [
    { title: "1. Lexical Analysis", desc: "Characters are scanned and converted into tokens.", key: "lexical" },
    { title: "2. Token Visualization", desc: "Inspect the token stream and scanner steps.", key: "tokens" },
    { title: "3. Symbol Table", desc: "View identifiers, types, scope, and initialization.", key: "symbols" },
    { title: "4. Syntax Analysis", desc: "Check the grammar of the source program.", key: "syntax" },
    { title: "5. Parse Tree", desc: "Explore the concrete syntax tree.", key: "tree" },
    { title: "6. Abstract Syntax Tree (AST)", desc: "Explore the simplified program structure.", key: "ast" },
    { title: "7. Semantic Analysis", desc: "Check declarations and identifier usage.", key: "semantic" },
    { title: "8. Intermediate Code", desc: "View three-address code.", key: "intermediate" },
    { title: "9. Quadruples and Triples", desc: "View intermediate-code representations.", key: "quadruples" },
    { title: "10. Basic Blocks and Control Flow", desc: "Explore basic blocks and control-flow edges.", key: "control" },
    { title: "11. Code Optimization", desc: "Compare code before and after optimization.", key: "optimization" },
    { title: "12. Target Code", desc: "View generated pseudo-assembly instructions.", key: "target" }
];

let current = 0;
let data = null;

const $ = id => document.getElementById(id);

const esc = value =>
    String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);

function showStatus(message, title = "Compilation Status") {
    $("status").textContent = message;
    if ($("statusTitle")) $("statusTitle").textContent = title;
}

function getErrors() {
    if (!data) return [];
    return [
        ...(data.lexical_errors || []),
        ...(data.syntax_errors || []),
        ...(data.semantic_errors || [])
    ];
}

function updateMetrics() {
    if (!data) {
        $("tokenCount").textContent = "0";
        $("variableCount").textContent = "0";
        $("blockCount").textContent = "0";
        $("instructionCount").textContent = "0";
        return;
    }

    $("tokenCount").textContent =
        (data.tokens || []).filter(t => t.type !== "EOF").length;

    $("variableCount").textContent = (data.symbols || []).length;
    $("blockCount").textContent = (data.basic_blocks || []).length;
    $("instructionCount").textContent = (data.target_code || []).length;
}

function table(headers, rows) {
    if (!rows || rows.length === 0) {
        return `<p class="muted">No data generated for this stage.</p>`;
    }

    return `
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>${headers.map(h => `<th>${esc(h)}</th>`).join("")}</tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>${row.map(value => `<td>${esc(value)}</td>`).join("")}</tr>
                    `).join("")}
                </tbody>
            </table>
        </div>`;
}

function listCode(items) {
    if (!items || items.length === 0) {
        return `<p class="muted">No code generated for this stage.</p>`;
    }

    return `<div class="code-list">${items.map((item, index) =>
        `${String(index + 1).padStart(2, "0")}  ${esc(
            typeof item === "object" ? JSON.stringify(item) : item
        )}`
    ).join("\n")}</div>`;
}

function treeHtml(node) {
    if (node === null || node === undefined) {
        return `<span>Empty</span>`;
    }

    if (typeof node !== "object") {
        return `<span>${esc(node)}</span>`;
    }

    if (Array.isArray(node)) {
        return `<ul>${node.map(child => `<li>${treeHtml(child)}</li>`).join("")}</ul>`;
    }

    const name = node.name ?? node.type ?? node.value ?? node.operator ?? "Node";
    const excluded = ["name", "type", "value", "operator"];
    const children = [];

    for (const [key, value] of Object.entries(node)) {
        if (excluded.includes(key) || value == null) continue;
        if (Array.isArray(value)) {
            children.push(...value.map(item => ({ label: key, item })));
        } else if (typeof value === "object") {
            children.push({ label: key, item: value });
        } else {
            children.push({ label: key, item: value });
        }
    }

    return `
        <div class="tree-node">
            <span>${esc(name)}</span>
            ${children.length ? `
                <ul>${children.map(child => `
                    <li>
                        <small>${esc(child.label)}</small>
                        ${treeHtml(child.item)}
                    </li>
                `).join("")}</ul>` : ""}
        </div>`;
}

function errorBox() {
    const errors = getErrors();
    if (!errors.length) return "";
    return `<div class="error"><strong>Diagnostics</strong><ul>
        ${errors.map(error => `<li>${esc(error)}</li>`).join("")}
    </ul></div>`;
}

function renderPhaseContent() {
    if (!data) {
        return `<div class="empty">
            <h3>Ready to compile</h3>
            <p>Enter a program and click Analyze Compiler to view the results.</p>
        </div>`;
    }

    const errors = errorBox();

    switch (phases[current].key) {
        case "lexical":
            return errors + table(
                ["#", "Token Type", "Lexeme", "Line", "Column"],
                (data.tokens || [])
                    .filter(t => t.type !== "EOF")
                    .map(t => [t.index, t.type, t.lexeme, t.line, t.column])
            );

        case "tokens":
            return `
                <h3>Token Stream</h3>
                ${listCode((data.tokens || [])
                    .filter(t => t.type !== "EOF")
                    .map(t => `${t.type} (${t.lexeme})`))}
                <h3>Scanner Steps</h3>
                ${table(
                    ["Step", "Lexeme", "Recognized As", "Line"],
                    (data.scanner_steps || []).map(s =>
                        [s.step, s.lexeme, s.recognized_as, s.line])
                )}`;

        case "symbols":
            return errors + table(
                ["Identifier", "Type", "Scope", "Initialized", "Line"],
                (data.symbols || []).map(s => [
                    s.name, s.type, s.scope,
                    s.initialized ? "Yes" : "No", s.line
                ])
            );

        case "syntax":
            return errors + (
                (data.syntax_errors || []).length
                    ? `<div class="error">Syntax analysis failed. Check the source program.</div>`
                    : `<div class="success">Syntax analysis completed without parser errors.</div>`
            ) + `<h3>Parser Trace</h3>${listCode(data.parser_trace || [])}`;

        case "tree":
            return errors + `<div class="tree">${treeHtml(data.parse_tree)}</div>`;

        case "ast":
            return errors + `
                <div class="tree">${treeHtml(data.ast)}</div>
                <h3>AST as JSON</h3>
                <div class="code-list">${esc(JSON.stringify(data.ast, null, 2))}</div>`;

        case "semantic":
            return errors + (
                (data.semantic_warnings || []).length
                    ? `<div class="warning"><strong>Warnings</strong><ul>
                        ${data.semantic_warnings.map(w => `<li>${esc(w)}</li>`).join("")}
                       </ul></div>`
                    : ""
            ) + (
                (data.semantic_errors || []).length
                    ? ""
                    : `<div class="success">No semantic errors detected.</div>`
            );

        case "intermediate":
            return `<h3>Three-Address Code (TAC)</h3>${listCode(data.tac || [])}`;

        case "quadruples":
            return `
                <h3>Quadruples</h3>
                ${table(
                    ["#", "Operator", "Argument 1", "Argument 2", "Result"],
                    (data.quadruples || []).map(q =>
                        [q.index, q.operator, q.arg1, q.arg2, q.result])
                )}
                <h3>Triples</h3>
                ${table(
                    ["#", "Operator", "Argument 1", "Argument 2"],
                    (data.triples || []).map(t =>
                        [t.index, t.operator, t.arg1, t.arg2])
                )}`;

        case "control":
            return `
                <h3>Basic Blocks</h3>
                ${(data.basic_blocks || []).map(block => `
                    <div class="block">
                        <h4>${esc(block.id)}</h4>
                        ${listCode(block.instructions || [])}
                        <p><strong>Successors:</strong>
                        ${esc((block.successors || []).join(", ") || "None")}</p>
                    </div>
                `).join("") || `<p class="muted">No basic blocks generated.</p>`}
                <h3>Control-Flow Graph Edges</h3>
                ${table(
                    ["From", "To"],
                    (data.cfg?.edges || []).map(edge => [edge.from, edge.to])
                )}`;

        case "optimization":
            return `
                <div class="two-col">
                    <div><h3>Before Optimization</h3>${listCode(data.tac || [])}</div>
                    <div><h3>After Optimization</h3>${listCode(data.optimized_tac || [])}</div>
                </div>
                <h3>Optimization Log</h3>
                ${listCode(data.optimization_log || [])}`;

        case "target":
            return `<h3>Generated Target Instructions</h3>${listCode(data.target_code || [])}`;

        default:
            return `<p class="muted">Select a compiler phase.</p>`;
    }
}

function renderTabs() {
    $("phaseNav").innerHTML = phases.map((phase, index) => `
        <button type="button"
            class="${index === current ? "active" : ""}"
            data-index="${index}">
            ${phase.title.replace(/^\d+\.\s*/, "")}
        </button>
    `).join("");

    $("phaseNav").querySelectorAll("button").forEach(button => {
        button.addEventListener("click", () => {
            current = Number(button.dataset.index);
            render();
        });
    });
}

function render() {
    renderTabs();

    $("phaseTitle").textContent = phases[current].title;
    $("phaseDesc").textContent = phases[current].desc;
    $("phaseContent").innerHTML = renderPhaseContent();

    $("prevBtn").disabled = current === 0;
    $("nextBtn").disabled = current === phases.length - 1;

    updateMetrics();
}

$("runBtn").addEventListener("click", async () => {
    const source = $("source").value.trim();

    if (!source) {
        showStatus("Please enter a program before compiling.", "Input Required");
        $("source").focus();
        return;
    }

    $("runBtn").disabled = true;
    showStatus("Compiling your program...", "Working");

    try {
        const response = await fetch("/compile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source })
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        data = await response.json();
        current = 0;

        const errors = getErrors();
        showStatus(
            errors.length
                ? `${errors.length} diagnostic(s) found. Review the compiler phases below.`
                : "Compilation pipeline completed successfully.",
            errors.length ? "Compilation Finished with Issues" : "Compilation Complete"
        );

        render();
    } catch (error) {
        console.error("Compilation error:", error);
        showStatus(
            "Could not compile. Check that Flask is running and inspect the terminal for errors.",
            "Compilation Failed"
        );
    } finally {
        $("runBtn").disabled = false;
    }
});

$("prevBtn").addEventListener("click", () => {
    if (current > 0) {
        current--;
        render();
    }
});

$("nextBtn").addEventListener("click", () => {
    if (current < phases.length - 1) {
        current++;
        render();
    }
});

$("exampleBtn").addEventListener("click", () => {
    $("source").value = `int a;
int b;
int c;

a = 10;
b = 20;
c = a + b * 2;

print(c);`;

    showStatus("Example loaded. Click Analyze Compiler to run it.", "Example Ready");
    $("source").focus();
});

$("clearBtn").addEventListener("click", () => {
    $("source").value = "";
    data = null;
    current = 0;
    showStatus("Enter a program and click Analyze Compiler.", "Ready to Analyze");
    render();
});

document.querySelectorAll(".sidebar .nav").forEach(button => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".sidebar .nav").forEach(item =>
            item.classList.remove("active")
        );
        button.classList.add("active");

        const phase = button.dataset.phase;

        if (phase === "overview" || phase === "source") {
            const target = phase === "source"
                ? $("source")
                : document.querySelector(".hero");
            target.scrollIntoView({ behavior: "smooth", block: "start" });
            if (phase === "source") $("source").focus();
            return;
        }

        const index = phases.findIndex(item => item.key === phase);
        if (index !== -1) {
            current = index;
            render();
            document.querySelector(".results").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    });
});

render();