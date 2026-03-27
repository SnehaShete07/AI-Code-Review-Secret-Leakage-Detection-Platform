from app.policies.engine import PolicyEngine


def test_policy_severity_computation():
    engine = PolicyEngine()
    result = engine.classify("secret", 0.95)
    assert result.severity in {"high", "critical"}
    assert result.cvss_score >= 0.1
    assert result.cvss_severity in {"low", "medium", "high", "critical"}


def test_merge_recommendation():
    engine = PolicyEngine()
    assert engine.merge_recommendation(["low", "critical"]) == "merge_blocked"
