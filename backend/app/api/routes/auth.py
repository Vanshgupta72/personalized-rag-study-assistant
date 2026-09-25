# Dependency used to identify the currently authenticated user.
from backend.app.services.auth_dependency import get_current_user

# FastAPI tools for creating routes, handling errors,
# and injecting dependencies.
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy database session.
from sqlalchemy.orm import Session

# Database session dependency.
from backend.app.db.database import get_db

# Request/response schemas.
from backend.app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

# User database operations.
from backend.app.services.user_service import (
    create_user,
    get_user_by_email
)

# Password verification function.
from backend.app.services.auth_service import verify_password

# JWT token generation.
from backend.app.services.jwt_service import create_access_token


# Router for authentication-related endpoints.
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    The password is hashed before it reaches the database.
    """

    # Check whether the email is already registered.
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create the new user.
    user = create_user(db, user_data)

    return user


@router.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate an existing user and return a JWT access token.
    """

    # Find the account using the supplied email.
    user = get_user_by_email(db, user_data.email)

    # Don't reveal whether the email exists.
    # Use the same authentication error for invalid credentials.
    if not user or not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate a token containing the authenticated user's ID.
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user = Depends(get_current_user)
):
    """
    Return the profile of the currently authenticated user.

    This endpoint is protected by JWT authentication.
    """

    return current_user