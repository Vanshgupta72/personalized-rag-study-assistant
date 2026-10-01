from datetime import datetime

from pydantic import BaseModel


class SubjectCreate(BaseModel):
    """
    Data received when a user creates a subject.
    """

    name: str


class SubjectResponse(BaseModel):
    """
    Data returned for a subject.
    """

    id: int
    user_id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}