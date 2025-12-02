"""
Pydantic response models for API endpoints.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class SummarizeResponse(BaseModel):
    """Response model for successful summarization."""

    model_config = ConfigDict(protected_namespaces=())

    summary: str = Field(
        description="Generated summary text with all 16 sections"
    )
    provider_used: str = Field(
        description="LLM provider that was used"
    )
    model_used: str = Field(
        description="Model name that was used"
    )
    files_processed: int = Field(
        description="Number of PDF files that were analyzed"
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(
        description="Error message"
    )
    detail: Optional[str] = Field(
        default=None,
        description="Additional error details"
    )


# Authentication Response Models

class UserResponse(BaseModel):
    """Response model for user data."""
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(description="User information")


# Project Response Models

class ProjectResponse(BaseModel):
    """Response model for project data."""
    id: UUID
    name: str
    client_name: str
    property_address: str
    status: str
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('status')
    def serialize_status(self, status, _info):
        """Convert ProjectStatus enum to string."""
        if hasattr(status, 'value'):
            return status.value
        return status


class ProjectListResponse(BaseModel):
    """Response model for list of projects."""
    projects: List[ProjectResponse]
    total: int


# Document Response Models

class DocumentResponse(BaseModel):
    """Response model for document data."""
    id: UUID
    filename: str
    file_size: int
    uploaded_at: datetime
    project_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Response model for list of documents."""
    documents: List[DocumentResponse]
    total: int


# Summary Response Models

class SummaryDocumentResponse(BaseModel):
    """Lightweight document info for summary."""
    id: UUID
    filename: str

    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    """Response model for summary data."""
    id: UUID
    summary_text: str
    provider_used: str
    model_used: str
    files_processed: int
    extra_prompt: Optional[str]
    created_at: datetime
    project_id: UUID
    documents: List[SummaryDocumentResponse]

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class SummaryListResponse(BaseModel):
    """Response model for list of summaries."""
    summaries: List[SummaryResponse]
    total: int
