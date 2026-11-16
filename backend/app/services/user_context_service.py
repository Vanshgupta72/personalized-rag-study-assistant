from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.models.subject import Subject
from backend.app.models.topic import Topic
from backend.app.models.learning_history import LearningHistory


def get_user_context(
    db: Session,
    user_id: int,
) -> dict:
    """
    Build a unified context object for the authenticated user.

    This context is intended to provide personalization information
    to the RAG and LLM layers.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found.")

    # ---------------------------------------------------------
    # USER PREFERENCES
    # ---------------------------------------------------------

    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    preference_context = {
        "learning_profile": (preferences.learning_profile or {}) if preferences else {},
        "preferred_language": (
            preferences.preferred_language
            if preferences
            else "English"
        ),
        "explanation_style": (
            preferences.explanation_style
            if preferences
            else "simple"
        ),
    }

    # ---------------------------------------------------------
    # SUBJECTS
    # ---------------------------------------------------------

    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == user_id)
        .order_by(Subject.name)
        .all()
    )

    subject_context = []

    for subject in subjects:

        topics = (
            db.query(Topic)
            .filter(Topic.subject_id == subject.id)
            .order_by(Topic.name)
            .all()
        )

        subject_context.append(
            {
                "id": subject.id,
                "name": subject.name,
                "topics": [
                    {
                        "id": topic.id,
                        "name": topic.name,
                    }
                    for topic in topics
                ],
            }
        )

    # ---------------------------------------------------------
    # LEARNING HISTORY
    # ---------------------------------------------------------

    history = (
        db.query(LearningHistory)
        .filter(LearningHistory.user_id == user_id)
        .order_by(LearningHistory.created_at.desc())
        .limit(20)
        .all()
    )

    history_context = [
        {
            "id": activity.id,
            "topic_id": activity.topic_id,
            "activity_type": activity.activity_type,
            "created_at": activity.created_at.isoformat(),
        }
        for activity in history
    ]

    # ---------------------------------------------------------
    # FINAL CONTEXT
    # ---------------------------------------------------------

    return {
        "user": {
            "id": user.id,
            "name": user.name,
        },
        "preferences": preference_context,
        "subjects": subject_context,
        "recent_learning_history": history_context,
    }
