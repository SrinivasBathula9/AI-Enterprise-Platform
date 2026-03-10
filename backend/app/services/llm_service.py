from functools import lru_cache
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama  # kept for Ollama provider support

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

    # Return the primary LLM directly.
    # NOTE: Do NOT wrap with .with_fallbacks(ollama) here — the Ollama fallback
    # strips the .bind_tools() bindings applied by the agent layer, which causes
    # tool calls (web_search, etc.) to silently vanish for any query that
    # triggers the fallback path.
    return _create_llm(provider, model)
