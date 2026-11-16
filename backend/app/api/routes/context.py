from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.services.auth_dependency import get_current_user
from backend.app.services.user_context_service import get_user_context


router = APIRouter(
    prefix="/context",
    tags=["User Context"],
)


@router.get("")
def get_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return the complete personalized context
    of the authenticated user.
    """

    return get_user_context(
        db=db,
        user_id=current_user.id,
    )