"""
Session API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.db.database import get_db
from app.modules.sessions import schemas, services, repositories
from app.core.permissions import get_current_user, require_role
from app.modules.auth.models import User

router = APIRouter()


@router.post("", response_model=schemas.SessionResponse)
async def create_session(
    request: schemas.SessionCreate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(require_role("agent", "admin"))
):
    """Create a new video session (Agent/Admin only)."""
    return await services.create_session(db, request.title, current_user.id)


@router.get("", response_model=List[schemas.SessionResponse])
def list_my_sessions(
    status: str = None,
    page: int = 1,
    per_page: int = 20,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(require_role("agent", "admin"))
):
    """List sessions created by the current agent."""
    skip = (page - 1) * per_page
    return repositories.list_sessions_for_agent(db, current_user.id, skip=skip, limit=per_page, status_filter=status)


@router.get("/{session_id}", response_model=schemas.SessionDetailResponse)
def get_session(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific session including stats."""
    session = repositories.get_session_with_stats(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if current_user.role == "customer" or (current_user.role == "agent" and session.agent_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
        
    return session


@router.get("/{session_id}/link", response_model=schemas.SessionJoinLinkResponse)
def get_session_join_link(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(require_role("agent", "admin"))
):
    """Get the customer join link for a session."""
    session = repositories.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if current_user.role == "agent" and session.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
        
    join_url = services.get_join_link(session)
    return {"join_url": join_url, "token": session.join_token}


@router.post("/{session_id}/end", response_model=schemas.SessionResponse)
async def end_session(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(require_role("agent", "admin"))
):
    """End a session and disconnect all participants."""
    return await services.end_session(db, session_id, current_user.id)


@router.get("/{session_id}/archive")
def download_session_archive(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(require_role("agent", "admin"))
):
    """Download a ZIP archive of the session chat history and media."""
    from fastapi.responses import StreamingResponse
    
    # Optional authorization check
    session = repositories.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if current_user.role == "agent" and session.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to archive this session")
        
    memory_file, filename = services.create_session_archive(db, session_id)
    
    return StreamingResponse(
        memory_file,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
