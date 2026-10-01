from pydantic import BaseModel


class PreferenceUpdate(BaseModel):
    """
    Data received when a user updates their study preferences.
    """

    preferred_language: str
    explanation_style: str


class PreferenceResponse(BaseModel):
    """
    Data returned when the user's study preferences are requested.
    """

    id: int
    user_id: int
    preferred_language: str
    explanation_style: str

    model_config = {"from_attributes": True}