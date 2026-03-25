from app.rules.js_rules import JavaScriptRiskyPatternRule
from app.rules.python_rules import PythonAstDangerousExecRule


def test_python_ast_rule_detects_eval():
    content = "x = eval(user_input)"
    rule = PythonAstDangerousExecRule()
    findings = rule.match("app.py", content)
    assert any(f.rule_id == "py.dangerous.exec" for f in findings)


def test_js_risky_pattern_detection():
    content = "const out = eval(input);"
    rule = JavaScriptRiskyPatternRule()
    findings = rule.match("index.js", content)
    assert findings
