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
    Delete a subject while preserving document metadata and learning history.
    """

    from backend.app.models.document import Document
    from backend.app.models.learning_history import LearningHistory
    from backend.app.models.topic import Topic

    try:
        # Find topics belonging to this subject.
        topics = (
            db.query(Topic)
            .filter(Topic.subject_id == subject.id)
            .all()
        )
        topic_ids = [topic.id for topic in topics]

        # Preserve documents by clearing their subject reference.
        db.query(Document).filter(
            Document.subject_id == subject.id
        ).update(
            {Document.subject_id: None},
            synchronize_session=False
        )

        if topic_ids:
            # Unlink documents from the topics being deleted.
            db.query(Document).filter(
                Document.topic_id.in_(topic_ids)
            ).update(
                {Document.topic_id: None},
                synchronize_session=False
            )

            # Keep learning-history records, but unlink deleted topics.
            db.query(LearningHistory).filter(
                LearningHistory.topic_id.in_(topic_ids)
            ).update(
                {LearningHistory.topic_id: None},
                synchronize_session=False
            )

            # Delete the now-unreferenced topics.
            for topic in topics:
                db.delete(topic)

            # Force topic DELETE statements to run before subject DELETE.
            db.flush()

        # Delete the subject after its references are cleared.
        db.delete(subject)
        db.commit()

    except Exception:
        db.rollback()
        raise
