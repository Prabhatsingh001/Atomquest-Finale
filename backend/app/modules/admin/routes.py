from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.livekit import LiveKitService, get_livekit
from app.core.permissions import require_role
from app.db.database import get_db
from app.modules.auth.models import User
from app.modules.sessions import repositories as session_repos
from app.modules.sessions import schemas as session_schemas

from . import schemas, services

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics", response_model=schemas.AdminMetricsResponse)
def get_metrics(
    db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))
):
    """Get system metrics.

    Args:
        db (Session): Database session dependency.
        current_user (User): The authenticated admin user dependency.

    Returns:
        schemas.AdminMetricsResponse: System metrics data.
    """
    return services.get_system_metrics(db)


@router.get("/sessions", response_model=List[session_schemas.SessionDetailResponse])
def get_sessions(
    status_filter: str = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all sessions with optional filtering.

    Args:
        status_filter (str, optional): Filter sessions by status. Defaults to None.
        page (int, optional): Page number for pagination. Defaults to 1.
        per_page (int, optional): Number of sessions per page. Defaults to 20.
        db (Session): Database session dependency.
        current_user (User): The authenticated admin user dependency.

    Returns:
        List[session_schemas.SessionDetailResponse]: List of session details.
    """
    skip = (page - 1) * per_page
    # Reusing the existing list_sessions_for_agent but bypassing agent check
    # Let's write a quick query here or add to repositories
    from app.modules.sessions.models import Session as DBSession

    query = db.query(DBSession)
    if status_filter:
        query = query.filter(DBSession.status == status_filter)

    sessions = (
        query.order_by(DBSession.created_at.desc()).offset(skip).limit(per_page).all()
    )
    # Populate stats for each
    result = []
    for s in sessions:
        result.append(session_repos.get_session_with_stats(db, s.id))
    return result


@router.post("/end-session")
async def force_end_session(
    req: schemas.ForceEndRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
    livekit: LiveKitService = Depends(get_livekit),
):
    """Force end a session.

    Args:
        req (schemas.ForceEndRequest): The request payload containing the session ID.
        db (Session): Database session dependency.
        current_user (User): The authenticated admin user dependency.
        livekit (LiveKitService): LiveKit service dependency.

    Returns:
        dict: A status dictionary indicating success.

    Raises:
        HTTPException: If the session is not found.
    """
    success = await services.force_end_session(db, livekit, req.session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}
