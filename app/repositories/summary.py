"""
Summary repository - database operations for Summary model
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import Summary, Document, Project


async def get_by_id(
    db: AsyncSession,
    summary_id: UUID,
    project_id: UUID,
    user_id: UUID
) -> Optional[Summary]:
    """Get summary by ID with ownership verification and linked documents"""
    result = await db.execute(
        select(Summary)
        .join(Project, Summary.project_id == Project.id)
        .where(
            Summary.id == summary_id,
            Summary.project_id == project_id,
            Project.user_id == user_id
        )
        .options(selectinload(Summary.documents))
    )
    return result.scalar_one_or_none()


async def get_all_for_project(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID
) -> List[Summary]:
    """List all summaries for a project with ownership verification"""
    # First verify user owns the project
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        return []

    # Get all summaries for the project with documents
    result = await db.execute(
        select(Summary)
        .where(Summary.project_id == project_id)
        .options(selectinload(Summary.documents))
        .order_by(Summary.created_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    document_ids: List[UUID],
    summary_text: str,
    provider_used: str,
    model_used: str,
    extra_prompt: Optional[str]
) -> Summary:
    """Create a new summary and link documents with ownership verification"""
    # Verify user owns the project
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project {project_id} not found or not owned by user")

    # Verify all documents belong to this project
    documents_result = await db.execute(
        select(Document)
        .where(
            Document.id.in_(document_ids),
            Document.project_id == project_id
        )
    )
    documents = list(documents_result.scalars().all())

    if len(documents) != len(document_ids):
        raise ValueError("Some documents not found or don't belong to this project")

    # Create summary
    summary = Summary(
        project_id=project_id,
        summary_text=summary_text,
        provider_used=provider_used,
        model_used=model_used,
        files_processed=len(document_ids),
        extra_prompt=extra_prompt,
    )

    # Link documents to summary
    summary.documents = documents

    db.add(summary)
    await db.commit()
    await db.refresh(summary, attribute_names=['documents'])
    return summary
