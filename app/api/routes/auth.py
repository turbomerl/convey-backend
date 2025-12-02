"""
Authentication routes - register, login, and user info
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...models.database import User
from ...models.request import RegisterRequest, LoginRequest
from ...models.response import TokenResponse, UserResponse
from ...services.auth import verify_password, create_access_token
from ...repositories import user as user_repo
from ..dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Register a new user

    Creates a new user account and returns an authentication token.
    """
    # Check if user already exists
    existing_user = await user_repo.get_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = await user_repo.create(
        db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Return token and user info
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Login with email and password

    Returns an authentication token if credentials are valid.
    """
    # Get user by email
    user = await user_repo.get_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Return token and user info
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get current user information

    Returns the authenticated user's profile information.
    """
    return UserResponse.model_validate(current_user)
