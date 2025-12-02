"""
Project repository - database operations for Project model
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import Project, ProjectStatus


async def get_by_id(db: AsyncSession, project_id: UUID, user_id: UUID) -> Optional[Project]:
    """Get project by ID for a specific user"""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == user_id)
        .options(selectinload(Project.documents), selectinload(Project.summaries))
    )
    return result.scalar_one_or_none()


async def get_all_for_user(db: AsyncSession, user_id: UUID) -> List[Project]:
    """Get all projects for a user"""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    client_name: str,
    property_address: str,
    status: ProjectStatus = ProjectStatus.DRAFT,
) -> Project:
    """Create a new project"""
    project = Project(
        user_id=user_id,
        name=name,
        client_name=client_name,
        property_address=property_address,
        status=status,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    **kwargs
) -> Optional[Project]:
    """Update project fields"""
    project = await get_by_id(db, project_id, user_id)
    if not project:
        return None

    for key, value in kwargs.items():
        if hasattr(project, key) and key not in ['id', 'user_id', 'created_at']:
            setattr(project, key, value)

    await db.commit()
    await db.refresh(project)
    return project
