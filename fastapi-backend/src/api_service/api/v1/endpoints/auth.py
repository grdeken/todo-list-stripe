"""Authentication endpoints for user registration and login."""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....core.security import create_access_token, get_password_hash, verify_password
from ....models import User
from ....schemas import PasswordChange, TokenResponse, UserCreate, UserLogin, UserResponse
from ...deps import CurrentUser, DatabaseSession

router = APIRouter()


def set_auth_cookie(response: Response, access_token: str) -> None:
    """
    Set authentication token in HttpOnly cookie for security.

    HttpOnly cookies prevent XSS attacks by making the token inaccessible to JavaScript.
    Secure flag ensures cookie is only sent over HTTPS in production.
    SameSite=lax prevents CSRF attacks while allowing normal navigation.

    Args:
        response: FastAPI Response object
        access_token: JWT access token to store
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="lax",  # CSRF protection
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert minutes to seconds
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, response: Response, db: DatabaseSession
) -> UserResponse:
    """
    Register a new user.

    Sets JWT token in HttpOnly cookie for secure authentication.

    Args:
        user_data: User registration data
        response: FastAPI response to set cookie
        db: Database session

    Returns:
        User information (token is set in HttpOnly cookie)

    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create access token and set in HttpOnly cookie
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    set_auth_cookie(response, access_token)

    return UserResponse.model_validate(db_user)


@router.post("/login", response_model=UserResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: DatabaseSession,
) -> UserResponse:
    """
    Login with email and password using OAuth2 password flow.

    Sets JWT token in HttpOnly cookie for secure authentication.

    Args:
        form_data: OAuth2 form data (username field contains email)
        response: FastAPI response to set cookie
        db: Database session

    Returns:
        User information (token is set in HttpOnly cookie)

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email (username field contains email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create access token and set in HttpOnly cookie
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    set_auth_cookie(response, access_token)

    return UserResponse.model_validate(user)


@router.post("/login-json", response_model=UserResponse)
async def login_json(
    user_data: UserLogin, response: Response, db: DatabaseSession
) -> UserResponse:
    """
    Login with email and password using JSON.

    Alternative endpoint for clients that prefer JSON over form data.
    Sets JWT token in HttpOnly cookie for secure authentication.

    Args:
        user_data: User login credentials
        response: FastAPI response to set cookie
        db: Database session

    Returns:
        User information (token is set in HttpOnly cookie)

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create access token and set in HttpOnly cookie
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    set_auth_cookie(response, access_token)

    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, current_user: CurrentUser) -> dict[str, str]:
    """
    Logout current user by clearing the HttpOnly authentication cookie.

    Args:
        response: FastAPI response to clear cookie
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # Clear the auth cookie
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
    )
    return {"message": "Successfully logged out"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, str]:
    """
    Change the current user's password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


