from app.rules.base import RuleMatch
from app.rules.registry import default_rules


class RuleScanner:
    def __init__(self) -> None:
        self.rules = default_rules()

    def scan_text(self, file_path: str, text: str) -> list[RuleMatch]:
        findings: list[RuleMatch] = []
        for rule in self.rules:
            findings.extend(rule.match(file_path, text))
        return findings
