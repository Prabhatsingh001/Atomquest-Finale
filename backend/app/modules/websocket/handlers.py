from app.db.database import SessionLocal
from app.modules.chat import services as chat_services
from app.modules.websocket.manager import manager


async def handle_message(session_id: int, user_id: int, data: dict):
    """Process incoming WebSocket messages based on their type.

    Args:
        session_id (int): The session where the message was received.
        user_id (int): The ID of the user who sent the message.
        data (dict): The parsed JSON payload of the message.

    Returns:
        None
    """
    msg_type = data.get("type")

    if msg_type == "chat":
        db = SessionLocal()
        try:
            msg = chat_services.send_message(
                db,
                session_id=session_id,
                sender_id=user_id,
                content=data.get("content"),
            )
            await manager.broadcast(
                session_id, {"type": "chat", "message": msg.model_dump(mode="json")}
            )
        finally:
            db.close()

    elif msg_type == "typing":
        await manager.broadcast(
            session_id,
            {
                "type": "typing",
                "user_id": user_id,
                "is_typing": data.get("is_typing", True),
            },
            exclude_user_id=user_id,
        )
