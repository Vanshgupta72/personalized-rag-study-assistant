from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.subject import SubjectCreate, SubjectResponse
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.subject_service import (
    create_subject,
    delete_subject,
    get_subject,
    get_user_subjects,
)


router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new subject for the authenticated user.
    """

    try:
        return create_subject(
            db=db,
            user_id=current_user.id,
            name=subject_data.name
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subject already exists."
        )


@router.get(
    "",
    response_model=list[SubjectResponse]
)
def list_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return only subjects belonging to the authenticated user.
    """

    return get_user_subjects(
        db=db,
        user_id=current_user.id
    )


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a subject only if it belongs to the authenticated user.
    """

    subject = get_subject(
        db=db,
        subject_id=subject_id,
        user_id=current_user.id
    )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found."
        )

    delete_subject(
        db=db,
        subject=subject
    )

    return None