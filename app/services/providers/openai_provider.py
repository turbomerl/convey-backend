"""
OpenAI provider implementation using Responses API.
"""
import io
from typing import List, Optional

from openai import OpenAI

from .base import BaseLLMProvider
from ..summarizer import DocumentInput, build_text_prompt
from ...config import settings


class OpenAIProvider(BaseLLMProvider):
    """OpenAI implementation using Responses API."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)

    def get_available_models(self) -> List[str]:
        """Return list of supported OpenAI models."""
        return ["gpt-4.1", "gpt-4.1-mini", "o4-mini", "gpt-5.1"]

    def summarize(
        self,
        documents: List[DocumentInput],
        model: str,
        extra_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate summary using OpenAI Responses API.

        Args:
            documents: List of PDF documents to analyze
            model: OpenAI model name
            extra_prompt: Optional additional instructions

        Returns:
            Generated summary text
        """
        if not documents:
            raise ValueError("At least one PDF document is required.")

        # Build attachments by uploading files to OpenAI
        attachments = self._build_attachments(documents)

        # Build text prompt with 16 sections
        text_prompt = build_text_prompt(extra_prompt)

        # Call OpenAI Responses API
        response = self.client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Review the attached lease/title pack and populate every section."},
                        *attachments,
                        text_prompt,
                    ],
                }
            ],
        )

        # Parse response
        return self._parse_response(response)

    def _build_attachments(self, documents: List[DocumentInput]) -> List[dict]:
        """
        Upload documents to OpenAI and return attachment references.

        Args:
            documents: List of documents to upload

        Returns:
            List of attachment dictionaries
        """
        attachments: List[dict] = []
        for document in documents:
            buffer = io.BytesIO(document.data)
            buffer.name = document.name  # type: ignore[attr-defined]
            file_obj = self.client.files.create(file=buffer, purpose="assistants")
            attachments.append(
                {
                    "type": "input_file",
                    "file_id": file_obj.id,
                }
            )
        return attachments

    def _parse_response(self, response) -> str:
        """
        Parse OpenAI response to extract text.

        Args:
            response: OpenAI API response object

        Returns:
            Extracted text
        """
        # Try simple attribute first
        if hasattr(response, "output_text"):
            return response.output_text

        # Try parsing structured response
        payload = response.model_dump()
        chunks: List[str] = []

        for item in payload.get("output", []) or []:
            item_type = item.get("type")
            if item_type == "output_text":
                text = item.get("text")
                if text:
                    chunks.append(text)
            elif item_type == "message":
                for block in item.get("content", []) or []:
                    if block.get("type") == "output_text" and block.get("text"):
                        chunks.append(block["text"])

        if chunks:
            return "\n\n".join(chunks).strip()

        return str(payload)
