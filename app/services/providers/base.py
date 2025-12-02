"""
Abstract base class for LLM providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..summarizer import DocumentInput


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def summarize(
        self,
        documents: List[DocumentInput],
        model: str,
        extra_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate summary from documents using provider's API.

        Args:
            documents: List of PDF documents to analyze
            model: Model name for the provider
            extra_prompt: Optional additional instructions

        Returns:
            Generated summary text
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Return list of supported model names for this provider.

        Returns:
            List of model names
        """
        pass
