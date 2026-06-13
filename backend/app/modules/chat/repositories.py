from sqlalchemy.orm import Session, joinedload

from app.modules.chat.models import Message


def create(
    db: Session,
    session_id: int,
    sender_id: int | None,
    content: str,
    message_type: str = "text",
) -> Message:
    """Create a new chat message in the database.

    Args:
        db (Session): Database session.
        session_id (int): ID of the session the message belongs to.
        sender_id (int | None): ID of the user sending the message, or None for system messages.
        content (str): The message payload/text.
        message_type (str, optional): The type of message (e.g., 'text', 'system'). Defaults to "text".

    Returns:
        Message: The created message object.
    """
    db_message = Message(
        session_id=session_id,
        sender_id=sender_id,
        content=content,
        message_type=message_type,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def list_by_session(
    db: Session, session_id: int, limit: int = 50, offset: int = 0
) -> list[Message]:
    """Retrieve all messages for a given session with optional pagination.

    Args:
        db (Session): Database session.
        session_id (int): The ID of the session.
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 50.
        offset (int, optional): Number of messages to skip. Defaults to 0.

    Returns:
        list[Message]: A list of message objects.
    """
    return (
        db.query(Message)
        .options(joinedload(Message.sender))
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
