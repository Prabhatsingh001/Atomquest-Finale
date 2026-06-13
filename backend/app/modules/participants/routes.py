"""
Participant API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.db.database import get_db
from app.modules.participants import schemas, services
from app.core.permissions import get_current_user, require_role
from app.modules.auth.models import User

router = APIRouter()


@router.post("/join/{token}", response_model=schemas.JoinResponse)
def customer_join(
    token: str, request: schemas.JoinRequest, db: DbSession = Depends(get_db)
):
    """Customer endpoint to join a session using a token.

    Creates an ephemeral customer user, adds them as a participant,
    and returns a LiveKit access token.

    Args:
        token (str): The secure join token for the session.
        request (schemas.JoinRequest): The request containing the customer's name.
        db (DbSession): Database session dependency.

    Returns:
        schemas.JoinResponse: Response data including the LiveKit token and session details.
    """
    return services.join_session(db, token, request.name)


@router.post("/session/{session_id}/join", response_model=schemas.JoinResponse)
def agent_join(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(require_role("agent", "admin")),
):
    """Agent endpoint to join a session they created.

    Allows an authorized agent or admin to join the LiveKit room.

    Args:
        session_id (int): The ID of the session to join.
        db (DbSession): Database session dependency.
        current_user (User): The authenticated agent/admin dependency.

    Returns:
        schemas.JoinResponse: Response data including the LiveKit token and session details.
    """
    # Extract name from email or profile (we just use email prefix for now)
    name = current_user.email.split("@")[0]
    return services.join_as_agent(db, session_id, current_user.id, name)
