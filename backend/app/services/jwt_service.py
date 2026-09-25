# datetime is used to define when the JWT token expires.
from datetime import datetime, timedelta, timezone

# PyJWT is used to create and decode JWT tokens.
import jwt

# Import our application settings.
from backend.app.core.config import settings


# Algorithm used to sign our JWT tokens.
# HS256 uses the application's secret key.
ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for an authenticated user.

    The user's ID is stored inside the token as the 'sub'
    (subject) claim.
    """

    # Calculate the expiration time of the token.
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    # JWT payload contains the information we want
    # to securely carry between requests.
    payload = {
        "sub": str(user_id),
        "exp": expires_at
    }

    # Sign the payload using our secret key.
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=ALGORITHM
    )

    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    PyJWT automatically checks the signature and expiration.
    """

    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[ALGORITHM]
    )