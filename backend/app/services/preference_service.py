from sqlalchemy.orm import Session

from backend.app.models.user_preference import UserPreference


def get_user_preferences(
    db: Session,
    user_id: int
) -> UserPreference | None:
    """
    Fetch the preferences belonging to a specific user.
    """

    return (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )


def create_user_preferences(
    db: Session,
    user_id: int,
    preferred_language: str,
    explanation_style: str
) -> UserPreference:
    """
    Create the initial preference record for a user.
    """

    preferences = UserPreference(
        user_id=user_id,
        preferred_language=preferred_language,
        explanation_style=explanation_style
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


def update_user_preferences(
    db: Session,
    preferences: UserPreference,
    preferred_language: str,
    explanation_style: str
) -> UserPreference:
    """
    Update an existing user's study preferences.
    """

    preferences.preferred_language = preferred_language
    preferences.explanation_style = explanation_style

    db.commit()
    db.refresh(preferences)

    return preferences