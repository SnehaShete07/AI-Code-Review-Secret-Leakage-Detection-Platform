from dataclasses import dataclass


@dataclass
class PolicyResult:
    severity: str
    score: int
    rationale: str


class PolicyEngine:
    CATEGORY_WEIGHTS = {
        "secret": 5,
        "injection": 5,
        "agent_security": 4,
        "prompt_security": 4,
        "auth": 3,
        "crypto": 3,
        "dependency_hygiene": 2,
        "general": 2,
    }

    def classify(self, category: str, confidence: float, override: str | None = None) -> PolicyResult:
        if override:
            return PolicyResult(override, 0, "Manual policy override applied")
        weight = self.CATEGORY_WEIGHTS.get(category, 2)
        score = round(weight * 20 + confidence * 20)
        if score >= 90:
            severity = "critical"
        elif score >= 75:
            severity = "high"
        elif score >= 55:
            severity = "medium"
        else:
            severity = "low"
        return PolicyResult(severity, score, f"Category weight={weight}, confidence={confidence:.2f}, score={score}")

    def merge_recommendation(self, severities: list[str]) -> str:
        if "critical" in severities:
            return "merge_blocked"
        if "high" in severities:
            return "needs_review"
        return "safe_to_merge"
