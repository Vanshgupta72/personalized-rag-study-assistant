from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PreferenceUpdate(BaseModel):
    """Study preferences aur onboarding answers."""

    preferred_language: str | None = None
    explanation_style: str | None = None
    learning_profile: dict[str, Any] | None = None
    onboarding_completed: bool | None = None


class PreferenceResponse(BaseModel):
    """User ki saved study preferences."""

    id: int
    user_id: int
    preferred_language: str
    explanation_style: str
    learning_profile: dict[str, Any] = Field(default_factory=dict)
    onboarding_completed: bool = False

    model_config = ConfigDict(from_attributes=True)

