from sqlalchemy.orm import Session
from app.modules.sessions.models import Session as DBSession, SessionStatus
from app.modules.participants.models import Participant
from app.modules.websocket.manager import manager
from app.core.livekit import LiveKitService
from app.modules.participants import repositories as participant_repos


def get_system_metrics(db: Session):
    """Retrieve system metrics across sessions, participants, and connections.

    Args:
        db (Session): Database session.

    Returns:
        dict: A dictionary containing metric counts.
    """
    active_sessions = (
        db.query(DBSession).filter(DBSession.status == SessionStatus.active).count()
    )
    total_sessions = db.query(DBSession).count()
    active_participants = (
        db.query(Participant).filter(Participant.left_at == None).count()
    )

    ws_connections = sum(len(conns) for conns in manager.active_connections.values())

    return {
        "active_sessions": active_sessions,
        "total_sessions": total_sessions,
        "active_participants": active_participants,
        "websocket_connections": ws_connections,
    }


async def force_end_session(db: Session, livekit: LiveKitService, session_id: int):
    """Force an active session to end, including LiveKit room deletion and websocket broadcast.

    Args:
        db (Session): Database session.
        livekit (LiveKitService): LiveKit service instance.
        session_id (int): The ID of the session to force end.

    Returns:
        bool: True if the session was successfully ended, False if the session was not found.
    """
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        return False

    # End LiveKit room
    try:
        await livekit.delete_room(session.room_name)
    except Exception:
        pass

    session.status = SessionStatus.completed
    db.commit()

    participants = participant_repos.list_by_session(db, session_id)
    for p in participants:
        participant_repos.mark_left(db, session_id, p.user_id)

    await manager.broadcast(
        session_id,
        {"type": "system", "content": "Session forcibly ended by administrator."},
    )

    return True
