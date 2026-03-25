import re

from app.rules.base import BaseRule, RuleMatch


class JavaScriptRiskyPatternRule(BaseRule):
    id = "js.risky.patterns"
    title = "Risky JavaScript execution pattern"
    category = "injection"

    PATTERNS = [
        (re.compile(r"\beval\s*\("), "Use of eval", "CWE-95"),
        (re.compile(r"new\s+Function\s*\("), "Use of Function constructor", "CWE-95"),
        (re.compile(r"child_process\.(exec|execSync)\s*\("), "Unsafe child_process execution", "CWE-78"),
    ]

    def match(self, file_path: str, content: str) -> list[RuleMatch]:
        if not any(file_path.endswith(ext) for ext in [".js", ".ts", ".tsx"]):
            return []
        matches: list[RuleMatch] = []
        for i, line in enumerate(content.splitlines(), start=1):
            for pattern, title, cwe in self.PATTERNS:
                if pattern.search(line):
                    matches.append(
                        RuleMatch(
                            title=title,
                            category=self.category,
                            rule_id=self.id,
                            file_path=file_path,
                            line_number=i,
                            snippet=line.strip(),
                            confidence=0.88,
                            cwe=cwe,
                        )
                    )
        return matches
