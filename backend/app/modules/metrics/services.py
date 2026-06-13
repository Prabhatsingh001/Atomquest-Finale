from prometheus_client import Gauge, Counter, Histogram

# Initialize metrics
ACTIVE_SESSIONS = Gauge(
    "atomquest_active_sessions", "Number of currently active sessions"
)
ACTIVE_PARTICIPANTS = Gauge(
    "atomquest_active_participants", "Number of currently active participants"
)
WEBSOCKET_CONNECTIONS = Gauge(
    "atomquest_websocket_connections", "Number of active WebSocket connections"
)

TOTAL_SESSIONS = Counter("atomquest_sessions_total", "Total number of created sessions")
TOTAL_RECORDINGS = Counter(
    "atomquest_recordings_total", "Total number of recordings started"
)
ERRORS_TOTAL = Counter("atomquest_errors_total", "Total number of application errors")

SESSION_DURATION = Histogram(
    "atomquest_session_duration_seconds", "Session duration in seconds"
)


def update_gauges(db_session, manager):
    """Called periodically or right before serving metrics to ensure gauges
    reflect the current state of the database and memory.

    Args:
        db_session (Session): The database session.
        manager (ConnectionManager): The WebSocket connection manager instance.

    Returns:
        None
    """
    from app.modules.sessions.models import Session as DBSession, SessionStatus
    from app.modules.participants.models import Participant

    # Active sessions
    active_count = (
        db_session.query(DBSession)
        .filter(DBSession.status == SessionStatus.active)
        .count()
    )
    ACTIVE_SESSIONS.set(active_count)

    # Active participants
    active_parts = (
        db_session.query(Participant).filter(Participant.left_at == None).count()
    )
    ACTIVE_PARTICIPANTS.set(active_parts)

    # Websocket connections
    ws_count = sum(len(conns) for conns in manager.active_connections.values())
    WEBSOCKET_CONNECTIONS.set(ws_count)
