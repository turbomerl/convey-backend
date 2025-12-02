"""
Provider factory for LLM providers.
"""
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider


def get_provider(provider_name: str) -> BaseLLMProvider:
    """
    Factory function to get provider instance.

    Args:
        provider_name: Name of the provider ("openai" or "gemini")

    Returns:
        Provider instance

    Raises:
        ValueError: If provider_name is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Supported providers: openai, gemini")


__all__ = ["get_provider", "BaseLLMProvider", "OpenAIProvider", "GeminiProvider"]
