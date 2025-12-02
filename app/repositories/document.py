"""
Document repository - database operations for Document model
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import Document, Project


async def get_by_id(
    db: AsyncSession,
    document_id: UUID,
    project_id: UUID,
    user_id: UUID
) -> Optional[Document]:
    """Get document by ID with ownership verification through project"""
    result = await db.execute(
        select(Document)
        .join(Project, Document.project_id == Project.id)
        .where(
            Document.id == document_id,
            Document.project_id == project_id,
            Project.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_all_for_project(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID
) -> List[Document]:
    """List all documents for a project with ownership verification"""
    # First verify user owns the project
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        return []

    # Get all documents for the project
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    filename: str,
    file_data: bytes
) -> Document:
    """Create a new document with ownership verification"""
    # Verify user owns the project
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project {project_id} not found or not owned by user")

    # Calculate file size
    file_size = len(file_data)

    # Create document
    document = Document(
        project_id=project_id,
        filename=filename,
        file_size=file_size,
        file_data=file_data,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def delete(
    db: AsyncSession,
    document_id: UUID,
    project_id: UUID,
    user_id: UUID
) -> bool:
    """Delete document with ownership verification"""
    # Get document with ownership check
    document = await get_by_id(db, document_id, project_id, user_id)
    if not document:
        return False

    await db.delete(document)
    await db.commit()
    return True
