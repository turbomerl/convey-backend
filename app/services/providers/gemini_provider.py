"""
Gemini provider stub implementation.
"""
from typing import List, Optional

from .base import BaseLLMProvider
from ..summarizer import DocumentInput


class GeminiProvider(BaseLLMProvider):
    """Gemini stub implementation - to be fully implemented later."""

    def get_available_models(self) -> List[str]:
        """Return list of supported Gemini models."""
        return ["gemini-pro", "gemini-pro-vision"]

    def summarize(
        self,
        documents: List[DocumentInput],
        model: str,
        extra_prompt: Optional[str] = None,
    ) -> str:
        """
        Placeholder for Gemini integration.

        Args:
            documents: List of PDF documents to analyze
            model: Gemini model name
            extra_prompt: Optional additional instructions

        Returns:
            Placeholder message
        """
        return """# Gemini Integration Coming Soon

Thank you for trying the Gemini provider! This feature is currently under development.

## What's Coming:
- Full Google Gemini API integration
- Support for gemini-pro and gemini-pro-vision models
- Same structured 16-section property analysis output
- Optimized prompts for Gemini models

## Current Status:
The Gemini provider architecture is in place and ready. We just need to complete the Google AI API integration.

## In the Meantime:
Please use the OpenAI provider for your property document analysis needs.

---
Provider: Gemini (Stub)
Model Requested: {model}
Documents Provided: {count}
""".format(model=model, count=len(documents))
