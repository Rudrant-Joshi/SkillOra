from services.code_intelligence.static_analyzers import (
    analyze,
    compute_quality_score,
    overall_severity,
)


def test_detects_eval_as_critical_security_issue():
    metrics, issues = analyze("python", "def f(x):\n    return eval(x)\n")
    security_issues = [i for i in issues if i.type == "security"]
    assert any(i.severity == "critical" for i in security_issues)


def test_detects_hardcoded_secret():
    code = 'API_KEY = "sk-1234567890abcdef"\n'
    _, issues = analyze("python", code)
    assert any("credential" in i.message.lower() for i in issues)


def test_bare_except_flagged_via_ast():
    code = "try:\n    x = 1\nexcept:\n    pass\n"
    _, issues = analyze("python", code)
    assert any("bare" in i.message.lower() for i in issues)


def test_clean_code_has_high_quality_score():
    code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    metrics, issues = analyze("python", code)
    score = compute_quality_score(metrics, issues)
    assert score >= 90


def test_syntax_error_reported_and_low_score():
    code = "def broken(:\n    pass\n"
    metrics, issues = analyze("python", code)
    assert any(i.severity == "critical" for i in issues)
    assert overall_severity(issues) == "critical"


def test_generic_fallback_for_unsupported_language():
    code = 'const x = eval("1+1");\n'
    metrics, issues = analyze("javascript", code)
    assert metrics.lines_of_code == 1
    assert any(i.type == "security" for i in issues)


def test_complexity_increases_with_branching():
    simple = "def f(x):\n    return x\n"
    branchy = (
        "def g(x):\n"
        "    if x > 0:\n"
        "        for i in range(x):\n"
        "            if i % 2 == 0:\n"
        "                try:\n"
        "                    pass\n"
        "                except ValueError:\n"
        "                    pass\n"
        "    return x\n"
    )
    _, s_issues = analyze("python", simple)
    _, b_issues = analyze("python", branchy)
    m_simple, _ = analyze("python", simple)
    m_branchy, _ = analyze("python", branchy)
    assert m_branchy.cyclomatic_complexity > m_simple.cyclomatic_complexity
