# SQLAlchemy session is used to communicate with PostgreSQL.
from sqlalchemy.orm import Session

# Import our User database model.
from backend.app.models.user import User

# Import the password hashing function.
from backend.app.services.auth_service import hash_password

# Import the data structure received during registration.
from backend.app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str):
    """
    Find a user using their email address.

    This is mainly used during registration and login
    to determine whether an account already exists.
    """

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user account.

    Steps:
    1. Hash the plain-text password.
    2. Create a User database object.
    3. Add it to the current database session.
    4. Commit the transaction.
    5. Refresh the object to get generated values such as ID.
    """

    # Convert the plain-text password into a secure Argon2 hash.
    password_hash = hash_password(user_data.password)

    # Create the SQLAlchemy User object.
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        name=user_data.name
    )

    # Add the new user to the current transaction.
    db.add(user)

    # Permanently save the transaction in PostgreSQL.
    db.commit()

    # Refresh the object so generated database values,
    # such as the auto-generated ID, are available.
    db.refresh(user)

    return user