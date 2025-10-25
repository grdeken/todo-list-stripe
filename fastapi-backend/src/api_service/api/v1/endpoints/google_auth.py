"""Google OAuth2 authentication endpoints."""
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....core.oauth import generate_state_token, oauth, verify_state_token
from ....core.security import create_access_token
from ....db import get_db
from ....models.oauth import OAuthAccount
from ....models.user import User

router = APIRouter()


def set_auth_cookie(response: Response, access_token: str) -> None:
    """
    Set authentication token in HttpOnly cookie for security.

    HttpOnly cookies prevent XSS attacks by making the token inaccessible to JavaScript.

    Args:
        response: FastAPI Response object
        access_token: JWT access token to store
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth2 login flow.

    Redirects the user to Google's OAuth2 authorization page.
    """
    # Generate state token for CSRF protection
    state = generate_state_token()

    # Store state in session (you might want to use Redis for production)
    request.session["oauth_state"] = state

    # Determine redirect URI based on environment
    redirect_uri = settings.GOOGLE_REDIRECT_URI or request.url_for("google_callback")

    # Redirect to Google OAuth2 authorization URL
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        state=state,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth2 callback.

    Processes the OAuth2 callback, creates or links user account,
    and returns a JWT token.
    """
    # Verify state token to prevent CSRF
    state = request.query_params.get("state")
    session_state = request.session.get("oauth_state")

    if not verify_state_token(state, session_state):
        raise HTTPException(status_code=400, detail="Invalid state token")

    # Clear the state from session
    request.session.pop("oauth_state", None)

    try:
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get access token: {str(e)}")

    # Get user info from Google
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")

    # Extract user information
    google_user_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if not google_user_id or not email:
        raise HTTPException(status_code=400, detail="Missing required user information")

    # Check if OAuth account already exists
    result = await db.execute(
        select(OAuthAccount)
        .where(OAuthAccount.provider == "google")
        .where(OAuthAccount.provider_user_id == google_user_id)
    )
    oauth_account = result.scalar_one_or_none()

    user: Optional[User] = None

    if oauth_account:
        # Existing OAuth account - get the associated user
        result = await db.execute(select(User).where(User.id == oauth_account.user_id))
        user = result.scalar_one_or_none()

        # Update OAuth tokens
        oauth_account.access_token = token.get("access_token")
        oauth_account.refresh_token = token.get("refresh_token")

        # Calculate token expiration
        expires_in = token.get("expires_in")
        if expires_in:
            oauth_account.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        oauth_account.scopes = json.dumps(settings.GOOGLE_OAUTH_SCOPES)
        oauth_account.updated_at = datetime.utcnow()

    else:
        # Check if user exists with this email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Create new user
            # Generate username from email or name
            username = email.split("@")[0]

            # Ensure username is unique
            base_username = username
            counter = 1
            while True:
                result = await db.execute(select(User).where(User.username == username))
                if not result.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                hashed_password=None,  # No password for OAuth users
                is_active=True,
            )
            db.add(user)
            await db.flush()  # Flush to get user.id

        # Create OAuth account
        expires_in = token.get("expires_in")
        token_expires_at = None
        if expires_in:
            token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        oauth_account = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=google_user_id,
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            token_expires_at=token_expires_at,
            provider_email=email,
            provider_name=name,
            provider_picture=picture,
            scopes=json.dumps(settings.GOOGLE_OAUTH_SCOPES),
        )
        db.add(oauth_account)

    await db.commit()
    await db.refresh(user)

    # Create JWT token for the user
    access_token = create_access_token(data={"sub": str(user.id)})

    # Redirect to frontend with token in HttpOnly cookie (not in URL for security)
    frontend_url = settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost:5173"
    redirect_url = f"{frontend_url}/auth/callback"

    # Create redirect response and set cookie
    response = RedirectResponse(url=redirect_url)
    set_auth_cookie(response, access_token)

    return response


@router.get("/google/refresh")
async def google_refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh Google OAuth2 access token.

    This endpoint can be used to refresh expired access tokens for Google Calendar API.
    """
    # TODO: Implement token refresh logic
    # This will be useful when implementing Google Calendar integration
    raise HTTPException(status_code=501, detail="Not implemented yet")
