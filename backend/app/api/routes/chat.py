from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.chat import ChatRequest, ChatResponse

from backend.app.services.auth_dependency import get_current_user
from backend.app.services.conversation_service import (
    add_message,
    create_conversation,
    get_conversation_messages,
)
from backend.app.services.learning_history_service import (
    create_learning_activity,
)
from backend.app.services.rag_service import answer_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------
    # SUBJECT VALIDATION
    # ---------------------------------------------------------

    if request.subject_id is not None:

        from backend.app.models.subject import Subject

        subject = (
            db.query(Subject)
            .filter(
                Subject.id == request.subject_id,
                Subject.user_id == current_user.id,
            )
            .first()
        )

        if not subject:
            raise HTTPException(
                status_code=404,
                detail="Subject not found.",
            )

    # ---------------------------------------------------------
    # TOPIC VALIDATION
    # ---------------------------------------------------------

    if request.topic_id is not None:

        from backend.app.models.topic import Topic

        topic = (
            db.query(Topic)
            .filter(
                Topic.id == request.topic_id,
            )
            .first()
        )

        if not topic:
            raise HTTPException(
                status_code=404,
                detail="Topic not found.",
            )

        if topic.subject_id != request.subject_id:
            raise HTTPException(
                status_code=400,
                detail="Topic does not belong to the selected subject.",
            )

        from backend.app.models.subject import Subject

        topic_subject = (
            db.query(Subject)
            .filter(
                Subject.id == topic.subject_id,
                Subject.user_id == current_user.id,
            )
            .first()
        )

        if not topic_subject:
            raise HTTPException(
                status_code=404,
                detail="Topic not found.",
            )

    # ---------------------------------------------------------
    # CONVERSATION
    # ---------------------------------------------------------

    conversation_id = request.conversation_id

    if conversation_id is not None:

        try:
            conversation_history = get_conversation_messages(
                db=db,
                conversation_id=conversation_id,
                user_id=current_user.id,
            )

        except ValueError:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

    else:

        conversation = create_conversation(
            db=db,
            user_id=current_user.id,
            title=request.question[:80],
        )

        conversation_id = conversation.id

        conversation_history = []

    # ---------------------------------------------------------
    # SAVE USER MESSAGE
    # ---------------------------------------------------------

    add_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=request.question,
    )

    # ---------------------------------------------------------
    # RAG + PERSONALIZATION
    # ---------------------------------------------------------

    result = answer_question(
        db=db,
        user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
        subject_id=request.subject_id,
        topic_id=request.topic_id,
        conversation_history=conversation_history,
    )

    answer = result["answer"]
    sources = result["sources"]

    # ---------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # ---------------------------------------------------------

    add_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
    )

    # ---------------------------------------------------------
    # LEARNING HISTORY
    # ---------------------------------------------------------

    create_learning_activity(
        db=db,
        user_id=current_user.id,
        topic_id=request.topic_id,
        activity_type="question_answered",
    )

    # ---------------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------------

    return {
        "conversation_id": conversation_id,
        "answer": answer,
        "sources": sources,
    }