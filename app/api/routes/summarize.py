"""
API routes for document summarization.
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from ...models.response import SummarizeResponse, ErrorResponse
from ...services.providers import get_provider
from ...services.summarizer import DocumentInput


router = APIRouter()


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Summarize property documents",
    description="Analyze multiple PDF files and generate a structured property report with 16 sections",
)
async def summarize_documents(
    pdfs: List[UploadFile] = File(..., description="PDF files to analyze"),
    provider: str = Form("openai", description="LLM provider: 'openai' or 'gemini'"),
    model: str = Form("gpt-4.1", description="Model name for the selected provider"),
    extra_prompt: str | None = Form(None, description="Optional additional instructions"),
) -> SummarizeResponse:
    """
    Summarize property documents using the specified LLM provider.

    Args:
        pdfs: List of PDF files to analyze
        provider: LLM provider to use (openai or gemini)
        model: Model name for the provider
        extra_prompt: Optional additional instructions

    Returns:
        SummarizeResponse with generated summary

    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    try:
        # Validate provider
        provider = provider.lower()
        if provider not in ["openai", "gemini"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider: {provider}. Must be 'openai' or 'gemini'",
            )

        # Validate PDFs
        if not pdfs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one PDF file is required",
            )

        # Read and validate PDF files
        documents: List[DocumentInput] = []
        for pdf in pdfs:
            # Check content type
            if pdf.content_type not in ["application/pdf", "application/octet-stream"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {pdf.filename} is not a PDF. Content type: {pdf.content_type}",
                )

            # Read file content
            content = await pdf.read()

            # Validate file is not empty
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {pdf.filename} is empty",
                )

            # Check file size (25MB limit)
            if len(content) > 25 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {pdf.filename} exceeds 25MB limit",
                )

            documents.append(DocumentInput(name=pdf.filename or "document.pdf", data=content))

        # Get provider instance
        try:
            llm_provider = get_provider(provider)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # Generate summary
        try:
            summary = llm_provider.summarize(
                documents=documents,
                model=model,
                extra_prompt=extra_prompt,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating summary: {str(e)}",
            )

        # Return response
        return SummarizeResponse(
            summary=summary,
            provider_used=provider,
            model_used=model,
            files_processed=len(documents),
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running",
)
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "property-summarizer-api"}
