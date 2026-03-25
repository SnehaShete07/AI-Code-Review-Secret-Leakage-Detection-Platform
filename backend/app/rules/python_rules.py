import ast

from app.rules.base import BaseRule, RuleMatch


class PythonAstDangerousExecRule(BaseRule):
    id = "py.dangerous.exec"
    title = "Dangerous dynamic execution"
    category = "injection"

    def match(self, file_path: str, content: str) -> list[RuleMatch]:
        if not file_path.endswith(".py"):
            return []
        matches: list[RuleMatch] = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = getattr(node.func, "id", "") or getattr(node.func, "attr", "")
                if fn in {"eval", "exec"}:
                    matches.append(
                        RuleMatch(
                            title=self.title,
                            category=self.category,
                            rule_id=self.id,
                            file_path=file_path,
                            line_number=getattr(node, "lineno", 1),
                            snippet=f"{fn}(...)",
                            confidence=0.95,
                            cwe="CWE-94",
                        )
                    )
                if fn == "loads" and getattr(node.func, "attr", "") == "loads" and "pickle" in ast.unparse(node.func.value):
                    matches.append(
                        RuleMatch(
                            title="Unsafe pickle deserialization",
                            category="injection",
                            rule_id="py.unsafe.pickle",
                            file_path=file_path,
                            line_number=getattr(node, "lineno", 1),
                            snippet="pickle.loads(...)",
                            confidence=0.9,
                            cwe="CWE-502",
                        )
                    )
        for i, line in enumerate(content.splitlines(), start=1):
            if "subprocess" in line and "shell=True" in line:
                matches.append(
                    RuleMatch(
                        title="subprocess with shell=True",
                        category="injection",
                        rule_id="py.subprocess.shell_true",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.92,
                        cwe="CWE-78",
                    )
                )
            if "verify=False" in line:
                matches.append(
                    RuleMatch(
                        title="TLS verification disabled",
                        category="crypto",
                        rule_id="py.tls.verify_false",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.83,
                        cwe="CWE-295",
                    )
                )
        return matches
