from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.permissions import get_current_user
from app.db.database import get_db
from app.modules.auth.models import User
from app.modules.chat import schemas, services
from app.modules.participants import repositories as participant_repos

router = APIRouter(prefix="/sessions/{session_id}/messages", tags=["chat"])


@router.get("", response_model=list[schemas.MessageResponse])
def get_messages(
    session_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve chat history for a session.

    Args:
        session_id (int): The ID of the session.
        limit (int, optional): Maximum messages to retrieve. Defaults to 50.
        offset (int, optional): Pagination offset. Defaults to 0.
        db (Session): Database session dependency.
        current_user (User): The authenticated user dependency.

    Returns:
        list[schemas.MessageResponse]: A list of message responses.

    Raises:
        HTTPException: If the user is a customer not participating in the session.
    """
    # Optional: verify if current_user is in the session or is admin/agent
    if current_user.role == "customer":
        participants = participant_repos.list_by_session(db, session_id)
        if current_user.id not in [p.user_id for p in participants]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a participant of this session",
            )

    return services.list_messages(db, session_id, limit, offset)
