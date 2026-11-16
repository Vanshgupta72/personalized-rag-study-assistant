from sqlalchemy.orm import Session

from backend.app.models.learning_history import LearningHistory


def create_learning_activity(
    db: Session,
    user_id: int,
    topic_id: int | None,
    activity_type: str
) -> LearningHistory:
    """
    Record a learning activity performed by a user.
    """

    activity = LearningHistory(
        user_id=user_id,
        topic_id=topic_id,
        activity_type=activity_type,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


def get_user_learning_history(
    db: Session,
    user_id: int
) -> list[LearningHistory]:
    """
    Return the user's learning activities,
    newest first.
    """

    return (
        db.query(LearningHistory)
        .filter(
            LearningHistory.user_id == user_id
        )
        .order_by(
            LearningHistory.created_at.desc()
        )
        .all()
    )


def get_topic_learning_history(
    db: Session,
    user_id: int,
    topic_id: int
) -> list[LearningHistory]:
    """
    Return learning activities for a specific
    topic belonging to the authenticated user.
    """

    return (
        db.query(LearningHistory)
        .filter(
            LearningHistory.user_id == user_id,
            LearningHistory.topic_id == topic_id,
        )
        .order_by(
            LearningHistory.created_at.desc()
        )
        .all()
    )