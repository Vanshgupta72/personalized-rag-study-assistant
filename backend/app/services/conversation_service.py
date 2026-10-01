from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.message import Message


def get_user_conversation(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> Conversation | None:
    """
    Return a conversation only if it belongs to the
    authenticated user.
    """

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .first()
    )


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> list[dict[str, str]]:
    """
    Return conversation messages in chronological order.
    """

    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not conversation:
        raise ValueError("Conversation not found.")

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


def create_conversation(
    db: Session,
    user_id: int,
    title: str,
) -> Conversation:
    """
    Create a new conversation for a user.
    """

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:
    """
    Add a message to an existing conversation.
    """

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message