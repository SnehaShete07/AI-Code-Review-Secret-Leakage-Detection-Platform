from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.mock import MockLLMProvider
from app.llm.openai_compatible import OpenAICompatibleProvider


def get_llm_provider() -> BaseLLMProvider:
    if settings.llm_provider == "openai":
        return OpenAICompatibleProvider()
    return MockLLMProvider()
