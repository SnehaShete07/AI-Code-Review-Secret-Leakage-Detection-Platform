from dataclasses import dataclass


@dataclass
class PolicyResult:
    severity: str
    score: int
    rationale: str
    cvss_score: float
    cvss_severity: str


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

    @staticmethod
    def cvss_severity(cvss_score: float) -> str:
        # FIRST CVSS qualitative ranges: None(0.0), Low(0.1-3.9), Medium(4.0-6.9), High(7.0-8.9), Critical(9.0-10.0)
        if cvss_score == 0.0:
            return "none"
        if cvss_score <= 3.9:
            return "low"
        if cvss_score <= 6.9:
            return "medium"
        if cvss_score <= 8.9:
            return "high"
        return "critical"

    def classify(self, category: str, confidence: float, override: str | None = None) -> PolicyResult:
        if override:
            return PolicyResult(override, 0, "Manual policy override applied", 0.0, "none")
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

        raw = min(10.0, max(0.1, (weight * 1.45) + (confidence * 2.6)))
        cvss_score = round(raw, 1)
        cvss_level = self.cvss_severity(cvss_score)
        return PolicyResult(
            severity,
            score,
            f"Category weight={weight}, confidence={confidence:.2f}, score={score}, cvss={cvss_score}",
            cvss_score,
            cvss_level,
        )

    def merge_recommendation(self, severities: list[str]) -> str:
        if "critical" in severities:
            return "merge_blocked"
        if "high" in severities:
            return "needs_review"
        return "safe_to_merge"
