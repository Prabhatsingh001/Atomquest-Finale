import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.db.database import SessionLocal
from app.core.security import decode_access_token
from app.modules.auth.models import User
from app.modules.websocket.manager import manager
from app.modules.websocket.handlers import handle_message
from app.modules.participants import repositories as participant_repos
from app.tasks.presence_tasks import set_online, set_offline

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, session_id: int, token: str = Query(...)
):
    """Handle WebSocket connections for a specific session.

    Authenticates the user via JWT token and manages the WebSocket lifecycle
    including answering messages and handling disconnections.

    Args:
        websocket (WebSocket): The WebSocket connection instance.
        session_id (int): The ID of the session to connect to.
        token (str): JWT authentication token provided as a query string.

    Returns:
        None
    """
    # Authenticate token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = int(user_id)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        participants = participant_repos.list_by_session(db, session_id)
        participant = next((p for p in participants if p.user_id == user_id), None)

        user_name = participant.name if participant else user.email
    finally:
        db.close()

    await manager.connect(websocket, session_id, user_id, user_name)
    set_online(session_id, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                json_data = json.loads(data)
                await handle_message(session_id, user_id, json_data)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        conn = manager.disconnect(websocket, session_id)
        if conn:
            set_offline(session_id, user_id)
            # We no longer broadcast 'left' immediately. The periodic task does it if grace expires.
