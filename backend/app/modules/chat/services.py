from sqlalchemy.orm import Session
from app.modules.chat import repositories
from app.modules.sessions import repositories as session_repos
from app.modules.participants import repositories as participant_repos
from fastapi import HTTPException, status
from app.modules.chat.schemas import MessageResponse


def format_message(
    db: Session, msg, session_id: int, participants_cache: dict = None
) -> MessageResponse:
    """Format a database message object into a structured response schema.

    Args:
        db (Session): Database session.
        msg (Message): The database message object.
        session_id (int): ID of the session the message belongs to.
        participants_cache (dict, optional): A cache of participant user_id to name mappings.
            Defaults to None, in which case it will be fetched.

    Returns:
        MessageResponse: The formatted message response.
    """
    sender_name = None
    sender_role = None

    if msg.sender_id:
        sender_role = msg.sender.role if msg.sender else None

        # use provided cache or fetch
        if participants_cache is None:
            participants = participant_repos.list_by_session(db, session_id)
            participants_cache = {p.user_id: p.name for p in participants}

        sender_name = participants_cache.get(msg.sender_id)

        if not sender_name and msg.sender:
            sender_name = msg.sender.email

    return MessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        sender_id=msg.sender_id,
        sender_name=sender_name,
        sender_role=sender_role,
        content=msg.content,
        message_type=msg.message_type,
        created_at=msg.created_at,
    )


def send_message(
    db: Session,
    session_id: int,
    sender_id: int | None,
    content: str,
    message_type: str = "text",
) -> MessageResponse:
    """Create and send a new message in a session.

    Args:
        db (Session): Database session.
        session_id (int): The ID of the targeted session.
        sender_id (int | None): The ID of the message sender.
        content (str): The message text content.
        message_type (str, optional): The type of message. Defaults to "text".

    Returns:
        MessageResponse: The newly created bounded message response.

    Raises:
        HTTPException: If the target session does not exist.
    """
    session = session_repos.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    msg = repositories.create(db, session_id, sender_id, content, message_type)

    # We need to refresh the sender relationship to have it accessible in format_message
    db.refresh(msg, ["sender"])
    return format_message(db, msg, session_id)


def list_messages(
    db: Session, session_id: int, limit: int = 50, offset: int = 0
) -> list[MessageResponse]:
    """List detailed chat messages for a session.

    Args:
        db (Session): Database session.
        session_id (int): The target session ID.
        limit (int, optional): The maximum number of messages. Defaults to 50.
        offset (int, optional): The index offset. Defaults to 0.

    Returns:
        list[MessageResponse]: A list of formatted responses.
    """
    messages = repositories.list_by_session(db, session_id, limit, offset)

    # Fetch participants once to use for name resolution
    participants = participant_repos.list_by_session(db, session_id)
    participants_cache = {p.user_id: p.name for p in participants}

    return [format_message(db, m, session_id, participants_cache) for m in messages]
