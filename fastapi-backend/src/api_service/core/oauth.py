"""Google OAuth2 integration."""
import secrets
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from .config import settings

# Initialize OAuth client
oauth = OAuth()

# Configure Google OAuth2
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    client_kwargs={
        "scope": " ".join(settings.GOOGLE_OAUTH_SCOPES),
    },
)


def generate_state_token() -> str:
    """Generate a random state token for CSRF protection."""
    return secrets.token_urlsafe(32)


def verify_state_token(state: str, session_state: Optional[str]) -> bool:
    """Verify the state token matches the session state."""
    if not session_state:
        return False
    return secrets.compare_digest(state, session_state)
