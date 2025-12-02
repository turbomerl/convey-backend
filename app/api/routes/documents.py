"""
Document routes - Upload, list, download, and delete documents for projects
"""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from ...database import get_db
from ...models.database import User
from ...models.response import DocumentResponse, DocumentListResponse
from ...repositories import document as document_repo
from ..dependencies import get_current_user

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])

# File upload constraints
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
ALLOWED_CONTENT_TYPES = {"application/pdf"}


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: UUID,
    file: Annotated[UploadFile, File(description="PDF file to upload")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Upload a document to a project

    Uploads a PDF file to the specified project. The file is stored in the database.
    Maximum file size is 25MB.
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF files are allowed.",
        )

    # Read file data
    file_data = await file.read()

    # Validate file size
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of 25MB",
        )

    # Create document
    try:
        document = await document_repo.create(
            db,
            project_id=project_id,
            user_id=current_user.id,
            filename=file.filename or "untitled.pdf",
            file_data=file_data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return DocumentResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    List all documents in a project

    Returns a list of all documents uploaded to the specified project.
    Only returns documents if the user owns the project.
    """
    documents = await document_repo.get_all_for_project(db, project_id, current_user.id)
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=len(documents),
    )


@router.get("/{document_id}/download")
async def download_document(
    project_id: UUID,
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Download a document

    Downloads the PDF file for the specified document.
    Returns 404 if document not found or user doesn't own the project.
    """
    document = await document_repo.get_by_id(db, document_id, project_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Create a BytesIO stream from the file data
    file_stream = BytesIO(document.file_data)

    # Return as streaming response
    return StreamingResponse(
        file_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{document.filename}"'
        },
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: UUID,
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a document

    Deletes the specified document from the project.
    Returns 404 if document not found or user doesn't own the project.
    """
    success = await document_repo.delete(db, document_id, project_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return None
