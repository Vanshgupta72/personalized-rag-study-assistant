# datetime is used to store the date and time
# when a user account is created.
from datetime import datetime

# SQLAlchemy column data types.
from sqlalchemy import DateTime, String

# Mapped and mapped_column are the modern SQLAlchemy
# way of defining typed database columns.
from sqlalchemy.orm import Mapped, mapped_column

# Base is the parent class for all our database models.
from backend.app.db.base import Base


class User(Base):
    """
    Represents a user account in the application.

    Each User object corresponds to one row
    in the PostgreSQL 'users' table.
    """

    # Tell SQLAlchemy which PostgreSQL table this model represents.
    __tablename__ = "users"

    # Unique identifier for every user.
    # primary_key=True makes this the table's primary key.
    # autoincrement=True lets PostgreSQL generate the ID automatically.
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # User's email address.
    # unique=True prevents duplicate email accounts.
    # nullable=False makes the field mandatory.
    # index=True improves lookup performance when searching by email.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # We never store the user's plain-text password.
    # The authentication system will hash the password,
    # and only this hash will be stored in the database.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User's display name.
    # Every account must have a name.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Date and time when the account was created.
    # datetime.utcnow is used automatically when a new
    # user record is inserted.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )