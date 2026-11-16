
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.conversation import Conversation
from backend.app.models.user import User
from backend.app.models.subject import Subject
from backend.app.models.topic import Topic
from backend.app.services.learning_history_service import (
    create_learning_activity,
)
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.conversation_service import (
    add_message,
    create_conversation,
    get_conversation_messages,
)
from backend.app.services.rag_service import answer_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/ask",
    response_model=ChatResponse,
)
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ask a question using the authenticated user's
    personalized study materials.

    Existing conversation history is loaded and passed
    to the RAG service for follow-up questions.
    """

    # Validate subject ownership before processing the question.
    if request.subject_id is not None:
        subject = (
            db.query(Subject)
            .filter(
                Subject.id == request.subject_id,
                Subject.user_id == current_user.id,
            )
            .first()
        )
        if subject is None:
            raise HTTPException(status_code=404, detail="Subject not found.")

    # A selected topic must belong to the selected subject.
    if request.topic_id is not None:
        if request.subject_id is None:
            raise HTTPException(
                status_code=400,
                detail="A subject must be selected with a topic.",
            )
        topic = (
            db.query(Topic)
            .filter(
                Topic.id == request.topic_id,
                Topic.subject_id == request.subject_id,
            )
            .first()
        )
        if topic is None:
            raise HTTPException(
                status_code=404,
                detail="Topic not found for this subject.",
            )

    # 1. Find an existing conversation or create a new one.
    if request.conversation_id is not None:

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        previous_messages = get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
            user_id=current_user.id,
        )

        # The conversation service returns dictionaries.
        conversation_history = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in previous_messages
        ]

    else:
        title = request.question.strip()[:60]

        conversation = create_conversation(
            db=db,
            user_id=current_user.id,
            title=title,
        )

        conversation_history = []

    # 2. Save the current user's question.
    add_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=request.question,
    )

    # 3. Run personalized RAG.
    result = answer_question(
        db=db,
        user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
        subject_id=request.subject_id,
        topic_id=request.topic_id,
        conversation_history=conversation_history,
    )

    # 4. Save the assistant's answer.
    add_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"],
    )

    # Record a question linked to the selected topic.
    if request.topic_id is not None:
        create_learning_activity(
            db=db,
            user_id=current_user.id,
            topic_id=request.topic_id,
            activity_type="question_asked",
        )

    # 5. Return the response.
    return {
        "conversation_id": conversation.id,
        "answer": result["answer"],
        "sources": result["sources"],
    }

