from datetime import datetime

from pydantic import BaseModel


class LearningHistoryResponse(BaseModel):
    id: int
    user_id: int
    topic_id: int | None = None
    activity_type: str
    created_at: datetime

    class Config:
        from_attributes = True