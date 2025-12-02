"""
Summary routes - Create and retrieve summaries for projects
"""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...models.database import User
from ...models.request import SummaryCreateRequest
from ...models.response import SummaryResponse, SummaryListResponse
from ...repositories import summary as summary_repo
from ...repositories import document as document_repo
from ...services.providers import get_provider
from ...services.summarizer import DocumentInput
from ..dependencies import get_current_user

router = APIRouter(prefix="/projects/{project_id}/summaries", tags=["summaries"])


@router.post("", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_summary(
    project_id: UUID,
    request: SummaryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new summary from existing documents

    Analyzes the specified documents using an LLM provider and creates a new summary.
    The documents must already be uploaded to the project.
    """
    # Fetch all specified documents with ownership verification
    documents = []
    for document_id in request.document_ids:
        doc = await document_repo.get_by_id(db, document_id, project_id, current_user.id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found or not accessible",
            )
        documents.append(doc)

    # Convert database documents to DocumentInput for summarizer
    document_inputs = [
        DocumentInput(name=doc.filename, data=doc.file_data)
        for doc in documents
    ]

    # Get LLM provider
    try:
        llm_provider = get_provider(request.provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Generate summary using LLM
    try:
        summary_text = llm_provider.summarize(
            documents=document_inputs,
            model=request.model,
            extra_prompt=request.extra_prompt,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}",
        )

    # Save summary to database
    try:
        summary = await summary_repo.create(
            db,
            project_id=project_id,
            user_id=current_user.id,
            document_ids=request.document_ids,
            summary_text=summary_text,
            provider_used=request.provider,
            model_used=request.model,
            extra_prompt=request.extra_prompt,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return SummaryResponse.model_validate(summary)


@router.get("", response_model=SummaryListResponse)
async def list_summaries(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    List all summaries in a project

    Returns a list of all summaries created for the specified project.
    Only returns summaries if the user owns the project.
    """
    summaries = await summary_repo.get_all_for_project(db, project_id, current_user.id)
    return SummaryListResponse(
        summaries=[SummaryResponse.model_validate(s) for s in summaries],
        total=len(summaries),
    )


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    project_id: UUID,
    summary_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific summary

    Returns the full summary details including the summary text and linked documents.
    Returns 404 if summary not found or user doesn't own the project.
    """
    summary = await summary_repo.get_by_id(db, summary_id, project_id, current_user.id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return SummaryResponse.model_validate(summary)
