"""User and authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from taskflow.models.base import get_db_session
from taskflow.services.auth_service import AuthService
from taskflow.services.user_service import UserService

router = APIRouter()
user_router = APIRouter()
security = HTTPBearer()


# Pydantic schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


# Dependency to get current user
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    request: UserRegisterRequest,
    db: Annotated[Session, Depends(get_db_session)],
):
    """Register a new user.

    Args:
        request: User registration data with email, password, and name
        db: Database session dependency

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: 400 if email already registered
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(
        email=request.email,
        name=request.name,
        password=request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
    )


@router.post("/login")
def login(
    request: UserLoginRequest,
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Authenticate user and return JWT access token.

    Parameters
    ----------
    request : UserLoginRequest
        Login credentials with email and password
    db : Session
        Database session

    Returns
    -------
    dict
        Dictionary with access_token and user info

    Raises
    ------
    HTTPException
        401 if authentication fails
    """
    auth_service = AuthService(db)
    result = auth_service.login(request.email, request.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Intentionally return dict instead of TokenResponse for inconsistency
    return result


@user_router.get("/me")
def get_current_user_info(
    current_user: Annotated[object, Depends(get_current_user)],
):
    # No docstring intentionally - showing inconsistent documentation
    # Manually build dict instead of using Pydantic model
    return {
        "id": current_user.id,  # type: ignore
        "email": current_user.email,  # type: ignore
        "name": current_user.name,  # type: ignore
        "is_active": current_user.is_active,  # type: ignore
    }


@user_router.patch("/me", response_model=UserResponse)
def update_current_user(
    request: UserUpdateRequest,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Update current user information."""
    user_service = UserService(db)
    updated_user = user_service.update_user(
        user_id=current_user.id,  # type: ignore
        name=request.name,
        email=request.email,
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user",
        )

    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        name=updated_user.name,
        is_active=updated_user.is_active,
    )


@user_router.get("/stats")
def get_user_stats(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get current user statistics."""
    user_service = UserService(db)
    stats = user_service.getUserStats(current_user.id)  # type: ignore - camelCase method
    return stats


@user_router.get("", response_model=list[UserResponse])
def get_all_users(
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get all active users for task assignment."""
    user_service = UserService(db)
    users = user_service.get_active_users()
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
        )
        for user in users
    ]
