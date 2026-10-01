from sqlalchemy.orm import Session

from backend.app.models.subject import Subject


def create_subject(
    db: Session,
    user_id: int,
    name: str
) -> Subject:
    """
    Create a subject belonging to the authenticated user.
    """

    subject = Subject(
        user_id=user_id,
        name=name.strip()
    )

    db.add(subject)
    db.commit()
    db.refresh(subject)

    return subject


def get_user_subjects(
    db: Session,
    user_id: int
) -> list[Subject]:
    """
    Return only the subjects belonging to the authenticated user.
    """

    return (
        db.query(Subject)
        .filter(Subject.user_id == user_id)
        .order_by(Subject.name.asc())
        .all()
    )


def get_subject(
    db: Session,
    subject_id: int,
    user_id: int
) -> Subject | None:
    """
    Fetch a subject only if it belongs to the authenticated user.
    """

    return (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == user_id
        )
        .first()
    )


def delete_subject(
    db: Session,
    subject: Subject
) -> None:
    """
    Delete a subject.
    """

    db.delete(subject)
    db.commit()