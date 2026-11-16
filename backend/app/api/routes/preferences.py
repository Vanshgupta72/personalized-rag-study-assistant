from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.preference import PreferenceResponse, PreferenceUpdate
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.preference_service import (
    create_user_preferences,
    get_user_preferences,
    update_user_preferences,
)

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("", response_model=PreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the authenticated user's study preferences."""

    preferences = get_user_preferences(db=db, user_id=current_user.id)

    if preferences is None:
        preferences = create_user_preferences(
            db=db,
            user_id=current_user.id,
            preferred_language="English",
            explanation_style="simple",
        )

    return preferences


@router.put("", response_model=PreferenceResponse)
def update_preferences(
    preference_data: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update only the preference fields supplied by the user."""

    preferences = get_user_preferences(db=db, user_id=current_user.id)

    if preferences is None:
        preferences = create_user_preferences(
            db=db,
            user_id=current_user.id,
            preferred_language=preference_data.preferred_language or "English",
            explanation_style=preference_data.explanation_style or "simple",
            learning_profile=preference_data.learning_profile or {},
            onboarding_completed=preference_data.onboarding_completed or False,
        )
    else:
        preferences = update_user_preferences(
            db=db,
            preferences=preferences,
            preferred_language=preference_data.preferred_language,
            explanation_style=preference_data.explanation_style,
            learning_profile=preference_data.learning_profile,
            onboarding_completed=preference_data.onboarding_completed,
        )

    return preferences
