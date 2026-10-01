from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    top_k: int = 3
    conversation_id: int | None = None
    subject_id: int | None = None
    topic_id: int | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: list