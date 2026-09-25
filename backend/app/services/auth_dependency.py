# FastAPI dependencies used for authentication.
from fastapi import Depends, HTTPException, status

# HTTPBearer extracts the token from:
# Authorization: Bearer <token>
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# SQLAlchemy session used to query PostgreSQL.
from sqlalchemy.orm import Session

# Database session dependency.
from backend.app.db.database import get_db

# User database model.
from backend.app.models.user import User

# JWT decoding function.
from backend.app.services.jwt_service import decode_access_token


# HTTPBearer tells FastAPI that this endpoint expects
# a Bearer token in the Authorization header.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Identify the currently authenticated user.

    Flow:
        Authorization header
            ↓
        Extract JWT
            ↓
        Decode + verify JWT
            ↓
        Extract user ID
            ↓
        Find user in PostgreSQL
    """

    token = credentials.credentials

    try:
        # Decode the JWT and verify its signature and expiration.
        payload = decode_access_token(token)

        # The 'sub' claim contains the authenticated user's ID.
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

    except Exception:
        # Do not expose internal JWT errors to the client.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Find the user represented by the token.
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user