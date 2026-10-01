from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.models.document import Document


# Directory where uploaded study materials will be stored.
UPLOAD_DIR = Path("data/uploads")

# Create the directory automatically if it does not exist.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# File types currently supported by the application.
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".pptx",
}


def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """
    Save an uploaded PDF or PPTX file to the uploads directory.

    A unique ID is added to the stored filename so that
    two users uploading files with the same original name
    do not overwrite each other.

    Returns:
        tuple[str, str]:
            - stored filename
            - original filename
    """

    # Get the original filename supplied by the client.
    original_filename = file.filename or ""

    # Extract the file extension.
    extension = Path(original_filename).suffix.lower()

    # Validate the file type.
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Only PDF and PPTX files are allowed."
        )

    # Generate a unique filename for storage.
    stored_filename = f"{uuid4().hex}{extension}"

    # Build the complete storage path.
    file_path = UPLOAD_DIR / stored_filename

    # Write the uploaded file to disk.
    with file_path.open("wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            buffer.write(chunk)

    return stored_filename, original_filename


def get_user_documents(
    db: Session,
    user_id: int
) -> list[Document]:
    """
    Return all documents belonging to a specific user.

    Documents are returned with the newest uploads first.
    """

    return (
        db.query(Document)
        .filter(
            Document.user_id == user_id
        )
        .order_by(
            Document.uploaded_at.desc()
        )
        .all()
    )


def get_user_document(
    db: Session,
    document_id: int,
    user_id: int
) -> Document | None:
    """
    Return a specific document only if it belongs
    to the authenticated user.
    """

    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id
        )
        .first()
    )


def delete_document(
    db: Session,
    document: Document
) -> None:
    """
    Delete a document record from PostgreSQL.

    Vector database and physical file cleanup
    will be handled separately.
    """

    db.delete(document)
    db.commit()