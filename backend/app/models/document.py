from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Document(Base):
    """
    Represents a document uploaded by a user.

    Each document belongs to exactly one user.
    The document metadata is stored in PostgreSQL,
    while the actual file will be stored separately.
    """

    __tablename__ = "documents"

    # Unique ID of the document.
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # ID of the user who uploaded this document.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Original filename uploaded by the user.
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Unique filename used to locate the actual file on disk.
    stored_filename: Mapped[str] = mapped_column(
    String(255),
    nullable=False
)

    # Human-readable title of the document.
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    subject_id: Mapped[int | None] = mapped_column(
    ForeignKey("subjects.id"),
    nullable=True,
    index=True
    )

    topic_id: Mapped[int | None] = mapped_column(
    ForeignKey("topics.id"),
    nullable=True,
    index=True
    )

    # File type such as pdf or pptx.
    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Time when the document was uploaded.
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )