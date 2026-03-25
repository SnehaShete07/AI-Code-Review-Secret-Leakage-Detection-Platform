import json

import httpx

from app.core.config import settings
from app.llm.base import BaseLLMProvider, LLMResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    def explain_finding(self, title: str, category: str, snippet: str) -> LLMResponse:
        if not settings.openai_api_key:
            raise ValueError("APP_OPENAI_API_KEY not set")
        prompt = {
            "title": title,
            "category": category,
            "snippet": snippet,
            "task": "Return strict JSON with keys explanation and remediation.",
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(
                f"{settings.openai_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": "You are a secure code reviewer."},
                        {"role": "user", "content": json.dumps(prompt)},
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return LLMResponse(
                explanation=data.get("explanation", "Security risk identified."),
                remediation=data.get("remediation", "Apply secure coding standards."),
            )
