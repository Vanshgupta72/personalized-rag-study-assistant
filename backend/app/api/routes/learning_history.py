from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.learning_history import (
    LearningHistoryResponse,
)
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.learning_history_service import (
    get_user_learning_history,
    get_topic_learning_history,
)


router = APIRouter(
    prefix="/learning-history",
    tags=["Learning History"],
)


@router.get(
    "",
    response_model=list[LearningHistoryResponse],
)
def get_learning_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return the complete learning history
    of the authenticated user.
    """

    return get_user_learning_history(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/topic/{topic_id}",
    response_model=list[LearningHistoryResponse],
)
def get_topic_history(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return learning activities for a specific topic.

    Only activities belonging to the authenticated
    user are returned.
    """

    return get_topic_learning_history(
        db=db,
        user_id=current_user.id,
        topic_id=topic_id,
    )