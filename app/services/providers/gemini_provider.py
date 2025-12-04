"""
Google Gemini provider implementation.
"""
import io
import time
from typing import List, Optional

import google.generativeai as genai

from .base import BaseLLMProvider
from ..summarizer import DocumentInput, build_text_prompt
from ...config import settings


class GeminiProvider(BaseLLMProvider):
    """Google Gemini implementation."""

    def __init__(self):
        """Initialize Gemini client."""
        if not settings.google_api_key:
            raise ValueError(
                "Google API key not configured. Set GOOGLE_API_KEY in environment."
            )
        # Configure the API key globally
        genai.configure(api_key=settings.google_api_key)

    def get_available_models(self) -> List[str]:
        """Return list of supported Gemini models."""
        return [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ]

    def summarize(
        self,
        documents: List[DocumentInput],
        model: str,
        extra_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate summary using Google Gemini API.

        Args:
            documents: List of PDF documents to analyze
            model: Gemini model name
            extra_prompt: Optional additional instructions

        Returns:
            Generated summary text
        """
        if not documents:
            raise ValueError("At least one PDF document is required.")

        # Upload documents to Gemini
        uploaded_files = self._upload_documents(documents)

        # Build text prompt with 16 sections
        text_prompt = build_text_prompt(extra_prompt)

        # Build contents list: instruction + files + structured prompt
        contents = [
            "Review the attached lease/title pack and populate every section.",
        ]

        # Add uploaded files
        contents.extend(uploaded_files)

        # Add structured prompt text
        contents.append(text_prompt["text"])

        # Create model instance and generate content
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(contents)

        # Extract and return text
        return self._parse_response(response)

    def _upload_documents(self, documents: List[DocumentInput]) -> List:
        """
        Upload documents to Gemini and return file references.

        Args:
            documents: List of documents to upload

        Returns:
            List of file objects for use in generate_content
        """
        uploaded_files = []
        for document in documents:
            # Create temporary file from bytes
            # genai.upload_file expects a file path, but we can pass a file-like object
            buffer = io.BytesIO(document.data)
            buffer.name = document.name

            # Upload to Gemini
            # Note: genai.upload_file returns a File object
            file = genai.upload_file(
                path=buffer,
                display_name=document.name,
                mime_type='application/pdf'
            )

            # Wait for processing if needed
            # Gemini needs to process PDFs before they can be used
            max_wait = 60  # Maximum 60 seconds
            elapsed = 0

            # Poll until the file is active
            while file.state.name == 'PROCESSING' and elapsed < max_wait:
                time.sleep(2)
                elapsed += 2
                file = genai.get_file(file.name)

            if file.state.name != 'ACTIVE':
                raise RuntimeError(
                    f"File {document.name} failed to process. State: {file.state.name}"
                )

            uploaded_files.append(file)

        return uploaded_files

    def _parse_response(self, response) -> str:
        """
        Parse Gemini response to extract text.

        Args:
            response: Gemini API response object

        Returns:
            Extracted text
        """
        # Try accessing text attribute directly
        if hasattr(response, 'text') and response.text:
            return response.text

        # Try extracting from candidates
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    # Extract text from content parts
                    parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            parts.append(part.text)
                    if parts:
                        return '\n\n'.join(parts)

        # Fallback: convert to string
        return str(response)
