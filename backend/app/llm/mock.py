from app.llm.base import BaseLLMProvider, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    def explain_finding(self, title: str, category: str, snippet: str) -> LLMResponse:
        redacted = snippet[:120].replace("\n", " ")
        return LLMResponse(
            explanation=f"{title} falls under {category}. The matched code was analyzed deterministically: '{redacted}'.",
            remediation="Replace insecure construct with validated input handling, remove hardcoded secrets, and add least-privilege guardrails.",
        )
