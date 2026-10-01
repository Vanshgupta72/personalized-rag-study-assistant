from datetime import datetime

from pydantic import BaseModel


class TopicCreate(BaseModel):
    name: str


class TopicResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }