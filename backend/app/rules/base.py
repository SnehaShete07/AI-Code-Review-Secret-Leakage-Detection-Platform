from dataclasses import dataclass


@dataclass
class RuleMatch:
    title: str
    category: str
    rule_id: str
    file_path: str
    line_number: int
    snippet: str
    confidence: float
    cwe: str | None


class BaseRule:
    id: str = "base.rule"
    title: str = "Base Rule"
    category: str = "general"

    def match(self, file_path: str, content: str) -> list[RuleMatch]:
        raise NotImplementedError
