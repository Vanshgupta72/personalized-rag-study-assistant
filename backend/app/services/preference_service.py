from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.user_preference import UserPreference


def get_user_preferences(
    db: Session,
    user_id: int
) -> UserPreference | None:
    """Fetch the preferences belonging to a specific user."""

    return (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )


def create_user_preferences(
    db: Session,
    user_id: int,
    preferred_language: str = "English",
    explanation_style: str = "simple",
    learning_profile: dict[str, Any] | None = None,
    onboarding_completed: bool = False,
) -> UserPreference:
    """Create the initial preference record for a user."""

    preferences = UserPreference(
        user_id=user_id,
        preferred_language=preferred_language,
        explanation_style=explanation_style,
        learning_profile=learning_profile or {},
        onboarding_completed=onboarding_completed,
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


def update_user_preferences(
    db: Session,
    preferences: UserPreference,
    preferred_language: str | None = None,
    explanation_style: str | None = None,
    learning_profile: dict[str, Any] | None = None,
    onboarding_completed: bool | None = None,
) -> UserPreference:
    """Update only the preference fields supplied by the caller."""

    if preferred_language is not None:
        preferences.preferred_language = preferred_language

    if explanation_style is not None:
        preferences.explanation_style = explanation_style

    if learning_profile is not None:
        preferences.learning_profile = learning_profile

    if onboarding_completed is not None:
        preferences.onboarding_completed = onboarding_completed

    db.commit()
    db.refresh(preferences)

    return preferences
