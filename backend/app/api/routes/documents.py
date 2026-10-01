from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.document import Document
from backend.app.models.subject import Subject
from backend.app.models.topic import Topic
from backend.app.models.user import User
from backend.app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
)
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.document_processing_service import (
    process_document,
)
from backend.app.services.document_service import (
    delete_document,
    get_user_document,
    get_user_documents,
    save_uploaded_file,
)
from backend.app.services.vector_service import (
    delete_document_chunks,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# =================================================
# UPLOAD DOCUMENT
# =================================================

@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    subject_id: int | None = Form(None),
    topic_id: int | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------
    # 1. Validate subject ownership
    # ---------------------------------------------

    subject = None

    if subject_id is not None:

        subject = (
            db.query(Subject)
            .filter(
                Subject.id == subject_id,
                Subject.user_id == current_user.id,
            )
            .first()
        )

        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found.",
            )

    # ---------------------------------------------
    # 2. Validate topic ownership
    # ---------------------------------------------

    topic = None

    if topic_id is not None:

        topic = (
            db.query(Topic)
            .join(
                Subject,
                Topic.subject_id == Subject.id,
            )
            .filter(
                Topic.id == topic_id,
                Subject.user_id == current_user.id,
            )
            .first()
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found.",
            )

        # Topic must belong to selected subject.
        if (
            subject_id is not None
            and topic.subject_id != subject_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Topic does not belong "
                    "to the selected subject."
                ),
            )

        # If only topic was provided,
        # automatically determine its subject.
        if subject_id is None:
            subject_id = topic.subject_id

    # ---------------------------------------------
    # 3. Save physical file
    # ---------------------------------------------

    try:

        stored_filename, original_filename = (
            save_uploaded_file(file)
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    # ---------------------------------------------
    # 4. Create PostgreSQL document record
    # ---------------------------------------------

    file_extension = (
        original_filename
        .rsplit(".", 1)[-1]
        .lower()
    )

    document = Document(
        user_id=current_user.id,
        filename=original_filename,
        stored_filename=stored_filename,
        title=original_filename.rsplit(".", 1)[0],
        file_type=file_extension,
        subject_id=subject_id,
        topic_id=topic_id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # ---------------------------------------------
    # 5. Process document
    #
    # Extraction
    #      ↓
    # Chunking
    #      ↓
    # Embeddings
    #      ↓
    # ChromaDB
    # ---------------------------------------------

    try:

        process_document(
            document_id=document.id,
            user_id=current_user.id,
            stored_filename=document.stored_filename,
            original_filename=document.filename,
            subject_id=document.subject_id,
            topic_id=document.topic_id,
        )

    except Exception as error:

        # Remove PostgreSQL record.
        db.delete(document)
        db.commit()

        # Remove physical file.
        file_path = (
            Path("data/uploads")
            / stored_filename
        )

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Document processing failed: {str(error)}"
            ),
        )

    return document


# =================================================
# LIST USER DOCUMENTS
# =================================================

@router.get(
    "",
    response_model=list[DocumentListResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all documents belonging to
    the authenticated user.
    """

    return get_user_documents(
        db=db,
        user_id=current_user.id,
    )


# =================================================
# GET SINGLE DOCUMENT
# =================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a single document only if it
    belongs to the authenticated user.
    """

    document = get_user_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


# =================================================
# DELETE DOCUMENT
# =================================================

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document from:

    1. Physical storage
    2. ChromaDB
    3. PostgreSQL
    """

    # ---------------------------------------------
    # 1. Find document belonging to current user
    # ---------------------------------------------

    document = get_user_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    # Save values before deleting the database object.
    stored_filename = document.stored_filename
    document_id = document.id

    # ---------------------------------------------
    # 2. Delete ChromaDB chunks
    # ---------------------------------------------

    delete_document_chunks(
        document_id=document_id
    )

    # ---------------------------------------------
    # 3. Delete physical file
    # ---------------------------------------------

    file_path = (
        Path("data/uploads")
        / stored_filename
    )

    if file_path.exists():
        file_path.unlink()

    # ---------------------------------------------
    # 4. Delete PostgreSQL record
    # ---------------------------------------------

    delete_document(
        db=db,
        document=document,
    )

    return None