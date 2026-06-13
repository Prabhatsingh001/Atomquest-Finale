"""
Database access for Sessions.
"""

from sqlalchemy.orm import Session as DbSession

from app.modules.sessions.models import Session


def create_session(db: DbSession, title: str, room_name: str, agent_id: int) -> Session:
    """Create a new video session.

    Args:
        db (DbSession): Database session.
        title (str): The title of the session.
        room_name (str): The LiveKit room name.
        agent_id (int): The ID of the agent creating the session.

    Returns:
        Session: The newly created session object.
    """
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
    """Retrieve a session by its ID.

    Args:
        db (DbSession): Database session.
        session_id (int): The ID of the session.

    Returns:
        Session | None: The session if found, else None.
    """
    return db.query(Session).filter(Session.id == session_id).first()


def get_session_by_token(db: DbSession, join_token: str) -> Session | None:
    """Retrieve a session by its unique join token.

    Args:
        db (DbSession): Database session.
        join_token (str): The unique join token.

    Returns:
        Session | None: The session if found, else None.
    """
    return db.query(Session).filter(Session.join_token == join_token).first()


def list_sessions_for_agent(
    db: DbSession,
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
) -> list[Session]:
    """List sessions created by an agent.

    Args:
        db (DbSession): Database session.
        agent_id (int): The ID of the agent.
        skip (int, optional): Pagination offset. Defaults to 0.
        limit (int, optional): The maximum number of sessions to return. Defaults to 100.
        status_filter (str, optional): A filter for session status (e.g. 'active'). Defaults to None.

    Returns:
        list[Session]: A list of session objects.
    """
    query = db.query(Session).filter(Session.agent_id == agent_id)
    if status_filter:
        query = query.filter(Session.status == status_filter)
    return query.order_by(Session.created_at.desc()).offset(skip).limit(limit).all()


def get_session_with_stats(db: DbSession, session_id: int):
    """Retrieve a session with calculated statistics (duration, message_count).

    Args:
        db (DbSession): Database session.
        session_id (int): The ID of the session.

    Returns:
        Session | None: The session object with populated stats, or None if not found.
    """
    from sqlalchemy.orm import joinedload

    from app.modules.chat.models import Message

    session = (
        db.query(Session)
        .options(joinedload(Session.participants))
        .filter(Session.id == session_id)
        .first()
    )
    if not session:
        return None

    message_count = db.query(Message).filter(Message.session_id == session_id).count()
    duration = 0
    if session.started_at and session.ended_at:
        duration = int((session.ended_at - session.started_at).total_seconds())
    elif session.started_at:
        from datetime import datetime, timezone

        # Use timezone aware comparison
        duration = int(
            (datetime.now(timezone.utc) - session.started_at).total_seconds()
        )

    setattr(session, "message_count", message_count)
    setattr(session, "duration_seconds", duration)
    return session
