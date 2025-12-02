"""
Pydantic request models for API endpoints.
"""
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, EmailStr


class SummarizeRequest(BaseModel):
    """Request model for summarize endpoint."""

    provider: str = Field(
        default="openai",
        description="LLM provider to use: 'openai' or 'gemini'"
    )
    model: str = Field(
        default="gpt-4.1",
        description="Model name for the selected provider"
    )
    extra_prompt: Optional[str] = Field(
        default=None,
        description="Optional additional instructions for the LLM"
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider is supported."""
        allowed = {"openai", "gemini"}
        if v.lower() not in allowed:
            raise ValueError(f"Provider must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name is not empty."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()


# Authentication Request Models

class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(description="User's email address")
    password: str = Field(min_length=8, description="User's password (minimum 8 characters)")
    full_name: str = Field(min_length=1, description="User's full name")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(description="User's email address")
    password: str = Field(description="User's password")


# Project Request Models

class ProjectCreateRequest(BaseModel):
    """Request model for creating a new project."""
    name: str = Field(min_length=1, max_length=255, description="Project name")
    client_name: str = Field(min_length=1, max_length=255, description="Client name")
    property_address: str = Field(min_length=1, description="Property address")
    status: Optional[str] = Field(
        default="draft",
        description="Project status: draft, in_progress, or completed"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> str:
        """Validate status is a valid enum value."""
        if v is None:
            return "draft"
        allowed = {"draft", "in_progress", "completed"}
        if v.lower() not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v.lower()


# Summary Request Models

class SummaryCreateRequest(BaseModel):
    """Request model for creating a new summary from documents."""
    document_ids: List[UUID] = Field(min_length=1, description="Documents to summarize")
    provider: str = Field(default="openai", description="LLM provider")
    model: str = Field(default="gpt-4.1", description="Model name")
    extra_prompt: Optional[str] = Field(default=None, description="Additional instructions")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider is supported."""
        if v.lower() not in {"openai", "gemini"}:
            raise ValueError("Provider must be openai or gemini")
        return v.lower()

    @field_validator("document_ids")
    @classmethod
    def validate_documents(cls, v: List[UUID]) -> List[UUID]:
        """Validate at least one document is selected."""
        if len(v) == 0:
            raise ValueError("Must select at least one document")
        return v
