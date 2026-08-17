"""
Deterministic static analysis. Per master prompt §4: "Do not use an LLM for
tasks that can reliably be solved with AST analysis, compiler output, static
analysis, complexity calculation, linting, dependency analysis."

This module is intentionally dependency-light (stdlib `ast` for Python) so
Phase 1 ships something real rather than a stub. Non-Python languages fall
back to language-agnostic heuristics (regex/line-based) — a real deployment
would plug in tree-sitter grammars per language here without changing the
service layer's contract.
"""
from __future__ import annotations

import ast
import re

from services.code_intelligence.schemas import ComplexityMetrics, Issue

_SECURITY_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"\beval\s*\("), "critical", "Use of eval() can execute arbitrary code."),
    (re.compile(r"\bexec\s*\("), "critical", "Use of exec() can execute arbitrary code."),
    (
        re.compile(r"subprocess\.(call|run|Popen)\([^)]*shell\s*=\s*True"),
        "high",
        "subprocess call with shell=True is vulnerable to shell injection.",
    ),
    (
        re.compile(r"\bpickle\.load[s]?\("),
        "high",
        "pickle.load on untrusted data can lead to arbitrary code execution.",
    ),
    (
        re.compile(r"(?i)(password|secret|api[_-]?key)\s*=\s*['\"][^'\"]{4,}['\"]"),
        "critical",
        "Possible hard-coded credential/secret.",
    ),
    (
        re.compile(r"md5\(|sha1\("),
        "medium",
        "MD5/SHA1 are weak for security-sensitive hashing (fine for non-crypto checksums).",
    ),
    (
        re.compile(r"\.execute\(\s*f['\"]|\.execute\(\s*['\"].*%s.*['\"]\s*%"),
        "high",
        "Possible SQL string interpolation — use parameterized queries.",
    ),
]

_SMELL_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"except\s*:\s*\n"), "Bare 'except:' silently swallows all exceptions."),
    (re.compile(r"#\s*TODO", re.I), "Unresolved TODO comment."),
    (re.compile(r"import \*"), "Wildcard import pollutes namespace and hides dependencies."),
]


def analyze_generic(code: str) -> tuple[ComplexityMetrics, list[Issue]]:
    """Language-agnostic fallback: line counts + regex-based smell/security scan."""
    lines = code.splitlines()
    issues: list[Issue] = []

    for pattern, severity, message in _SECURITY_PATTERNS:
        for m in pattern.finditer(code):
            line_no = code[: m.start()].count("\n") + 1
            issues.append(
                Issue(type="security", severity=severity, line=line_no, message=message,
                      source="static_analysis")
            )

    for pattern, message in _SMELL_PATTERNS:
        for m in pattern.finditer(code):
            line_no = code[: m.start()].count("\n") + 1
            issues.append(
                Issue(type="smell", severity="low", line=line_no, message=message,
                      source="static_analysis")
            )

    metrics = ComplexityMetrics(lines_of_code=len(lines))
    return metrics, issues


def analyze_python(code: str) -> tuple[ComplexityMetrics, list[Issue]]:
    """AST-based analysis for Python: complexity, nesting depth, long functions."""
    issues: list[Issue] = []
    lines = code.splitlines()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues.append(
            Issue(
                type="bug", severity="critical", line=e.lineno,
                message=f"SyntaxError: {e.msg}", source="static_analysis",
            )
        )
        metrics = ComplexityMetrics(lines_of_code=len(lines))
        return metrics, issues

    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    long_functions = []
    max_nesting = 0
    total_complexity = 1  # base complexity

    for fn in functions:
        fn_lines = (fn.end_lineno or fn.lineno) - fn.lineno + 1
        if fn_lines > 60:
            long_functions.append(f"{fn.name} (~{fn_lines} lines)")
            issues.append(
                Issue(
                    type="smell", severity="medium", line=fn.lineno,
                    message=f"Function '{fn.name}' is {fn_lines} lines long; consider splitting.",
                    source="static_analysis",
                )
            )
        max_nesting = max(max_nesting, _max_nesting_depth(fn))
        total_complexity += _cyclomatic_complexity(fn)

    if max_nesting > 4:
        issues.append(
            Issue(
                type="smell", severity="medium", line=None,
                message=f"Deep nesting detected (depth {max_nesting}); consider early returns.",
                source="static_analysis",
            )
        )

    # bare except via AST (more reliable than regex for Python)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(
                Issue(
                    type="smell", severity="low", line=node.lineno,
                    message="Bare 'except:' silently swallows all exceptions.",
                    source="static_analysis",
                )
            )

    _, generic_issues = analyze_generic(code)
    # avoid double-reporting bare except from regex pass
    generic_issues = [i for i in generic_issues if "Bare 'except:'" not in i.message]
    issues.extend(generic_issues)

    metrics = ComplexityMetrics(
        cyclomatic_complexity=total_complexity,
        lines_of_code=len(lines),
        max_nesting_depth=max_nesting,
        function_count=len(functions),
        long_functions=long_functions,
    )
    return metrics, issues


def _cyclomatic_complexity(node: ast.AST) -> int:
    complexity = 0
    for child in ast.walk(node):
        if isinstance(
            child,
            (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.BoolOp,
             ast.ExceptHandler),
        ):
            complexity += 1
        elif isinstance(child, ast.comprehension):
            complexity += 1
    return complexity


def _max_nesting_depth(node: ast.AST, depth: int = 0) -> int:
    max_depth = depth
    nesting_nodes = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With)
    for child in ast.iter_child_nodes(node):
        child_depth = depth + 1 if isinstance(child, nesting_nodes) else depth
        max_depth = max(max_depth, _max_nesting_depth(child, child_depth))
    return max_depth


def compute_quality_score(metrics: ComplexityMetrics, issues: list[Issue]) -> int:
    """
    Deterministic, explainable quality score (0-100). Starts at 100 and
    applies weighted deductions — no black-box ML for something this
    rule-derivable (master prompt §4).
    """
    score = 100
    severity_penalty = {"critical": 25, "high": 15, "medium": 7, "low": 2}
    for issue in issues:
        score -= severity_penalty.get(issue.severity, 2)

    if metrics.cyclomatic_complexity and metrics.cyclomatic_complexity > 20:
        score -= min(20, (metrics.cyclomatic_complexity - 20))
    if metrics.max_nesting_depth and metrics.max_nesting_depth > 4:
        score -= (metrics.max_nesting_depth - 4) * 3

    return max(0, min(100, score))


def overall_severity(issues: list[Issue]) -> str:
    order = ["critical", "high", "medium", "low"]
    present = {i.severity for i in issues}
    for level in order:
        if level in present:
            return level
    return "none"


LANGUAGE_ANALYZERS = {
    "python": analyze_python,
}


def analyze(language: str, code: str) -> tuple[ComplexityMetrics, list[Issue]]:
    analyzer = LANGUAGE_ANALYZERS.get(language.lower(), analyze_generic)
    return analyzer(code)
