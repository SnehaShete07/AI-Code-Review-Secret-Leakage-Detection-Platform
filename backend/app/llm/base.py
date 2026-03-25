from dataclasses import dataclass


@dataclass
class LLMResponse:
    explanation: str
    remediation: str


class BaseLLMProvider:
    def explain_finding(self, title: str, category: str, snippet: str) -> LLMResponse:
        raise NotImplementedError
