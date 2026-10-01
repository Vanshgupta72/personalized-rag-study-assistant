from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class User(Base):
    """
    Represents a user account in the application.

    Each User object corresponds to one row
    in the PostgreSQL 'users' table.
    """

    __tablename__ = "users"

    # Unique ID of the user.
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # User's email address.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Securely hashed password.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User's display name.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Account creation timestamp.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )