from functools import lru_cache
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from app.config import get_settings

settings = get_settings()

ProviderType = Literal["anthropic", "openai", "ollama"]

# Default models per provider
DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-3-5-sonnet-20240620",
    "openai": "gpt-4o",
    "ollama": "llama3.1:8b",
}


def get_llm(
    provider: ProviderType | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    streaming: bool = True,
) -> BaseChatModel:
    provider = provider or settings.default_llm_provider
    model = model or DEFAULT_MODELS.get(provider, settings.default_llm_model)

    def _create_llm(p: str, m: str) -> BaseChatModel:
        if p == "anthropic":
            return ChatAnthropic(
                model=m,
                api_key=settings.anthropic_api_key,
                temperature=temperature,
                streaming=streaming,
            )
        elif p == "openai":
            return ChatOpenAI(
                model=m,
                api_key=settings.openai_api_key,
                temperature=temperature,
                streaming=streaming,
            )
        elif p == "ollama":
            return ChatOllama(
                model=m,
                base_url=settings.ollama_base_url,
                temperature=temperature,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {p}")

    # Create the primary LLM
    primary_llm = _create_llm(provider, model)

    # If it's a paid provider, add a fallback chain
    if provider in ["anthropic", "openai"]:
        # Primary fallback: llama3.1:8b on Ollama
        fallback_llm_1 = ChatOllama(
            model="llama3.1:8b",
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )
        return primary_llm.with_fallbacks([fallback_llm_1])

    return primary_llm
