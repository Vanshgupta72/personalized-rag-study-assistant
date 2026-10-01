from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    stored_filename: str
    title: str
    file_type: str
    subject_id: int | None
    topic_id: int | None
    uploaded_at: datetime
    chunk_count: int | None = None

    model_config = {
        "from_attributes": True
    }


class DocumentListResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    title: str
    file_type: str
    subject_id: int | None
    topic_id: int | None
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }