from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.subject import Subject
from backend.app.models.user import User
from backend.app.schemas.topic import TopicCreate, TopicResponse
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.topic_service import (
    create_topic,
    delete_topic,
    get_subject_topics,
    get_topic,
)


router = APIRouter(
    prefix="/subjects/{subject_id}/topics",
    tags=["Topics"]
)


@router.post(
    "",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_topic(
    subject_id: int,
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Make sure the subject belongs to the
    # currently authenticated user.
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        )
        .first()
    )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found."
        )

    try:
        return create_topic(
            db=db,
            subject_id=subject_id,
            name=topic_data.name
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Topic already exists."
        )


@router.get(
    "",
    response_model=list[TopicResponse]
)
def list_topics(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # First verify that this subject belongs
    # to the authenticated user.
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        )
        .first()
    )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found."
        )

    return get_subject_topics(
        db=db,
        subject_id=subject_id
    )


@router.delete(
    "/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_topic(
    subject_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify subject ownership first.
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        )
        .first()
    )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found."
        )

    topic = get_topic(
        db=db,
        topic_id=topic_id,
        subject_id=subject_id
    )

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found."
        )

    delete_topic(
        db=db,
        topic=topic
    )

    return None