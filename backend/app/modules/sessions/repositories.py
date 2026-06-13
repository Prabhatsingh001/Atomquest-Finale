"""
Database access for Sessions.
"""
from sqlalchemy.orm import Session as DbSession
from app.modules.sessions.models import Session


def create_session(db: DbSession, title: str, room_name: str, agent_id: int) -> Session:
    """Create a new video session."""
    session = Session(
        title=title,
        room_name=room_name,
        agent_id=agent_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DbSession, session_id: int) -> Session | None:
    """Retrieve a session by its ID."""
    return db.query(Session).filter(Session.id == session_id).first()


def get_session_by_token(db: DbSession, join_token: str) -> Session | None:
    """Retrieve a session by its unique join token."""
    return db.query(Session).filter(Session.join_token == join_token).first()


def list_sessions_for_agent(db: DbSession, agent_id: int, skip: int = 0, limit: int = 100, status_filter: str = None) -> list[Session]:
    """List sessions created by an agent."""
    query = db.query(Session).filter(Session.agent_id == agent_id)
    if status_filter:
        query = query.filter(Session.status == status_filter)
    return query.order_by(Session.created_at.desc()).offset(skip).limit(limit).all()

def get_session_with_stats(db: DbSession, session_id: int):
    from sqlalchemy.orm import joinedload
    from app.modules.chat.models import Message
    
    session = db.query(Session).options(joinedload(Session.participants)).filter(Session.id == session_id).first()
    if not session:
        return None
        
    message_count = db.query(Message).filter(Message.session_id == session_id).count()
    duration = 0
    if session.started_at and session.ended_at:
        duration = int((session.ended_at - session.started_at).total_seconds())
    elif session.started_at:
        from datetime import datetime, timezone
        # Use timezone aware comparison
        duration = int((datetime.now(timezone.utc) - session.started_at).total_seconds())
        
    setattr(session, 'message_count', message_count)
    setattr(session, 'duration_seconds', duration)
    return session
