"""
Project routes - CRUD operations for projects
"""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...models.database import User, ProjectStatus
from ...models.request import ProjectCreateRequest
from ...models.response import ProjectResponse, ProjectListResponse
from ...repositories import project as project_repo
from ..dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new project

    Creates a new project for the authenticated user.
    """
    # Convert status string to enum
    status_enum = ProjectStatus[request.status.upper()]

    project = await project_repo.create(
        db,
        user_id=current_user.id,
        name=request.name,
        client_name=request.client_name,
        property_address=request.property_address,
        status=status_enum,
    )

    return ProjectResponse.model_validate(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get all projects for current user

    Returns a list of all projects owned by the authenticated user.
    """
    projects = await project_repo.get_all_for_user(db, current_user.id)
    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=len(projects),
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific project

    Returns project details if the project belongs to the authenticated user.
    """
    project = await project_repo.get_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectResponse.model_validate(project)
