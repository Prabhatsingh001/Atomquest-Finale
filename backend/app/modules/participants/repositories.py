"""
Database access for Participants.
"""

from sqlalchemy.orm import Session

from app.modules.participants.models import Participant


def create_participant(
    db: Session, session_id: int, user_id: int, identity: str, name: str
) -> Participant:
    """Create a new participant record.

    Args:
        db (Session): Database session.
        session_id (int): The ID of the session the participant is joining.
        user_id (int): The ID of the user joining the session.
        identity (str): The LiveKit identity string.
        name (str): The display name of the participant.

    Returns:
        Participant: The newly created participant object.
    """
    participant = Participant(
        session_id=session_id,
        user_id=user_id,
        identity=identity,
        name=name,
        is_connected=False,
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def get_by_identity(db: Session, identity: str) -> Participant | None:
    """Retrieve a participant by their LiveKit identity.

    Args:
        db (Session): Database session.
        identity (str): The LiveKit identity of the participant.

    Returns:
        Participant | None: The participant object if found, otherwise None.
    """
    return db.query(Participant).filter(Participant.identity == identity).first()


def mark_left(db: Session, session_id: int, user_id: int) -> None:
    """Mark a participant as disconnected and record their departure time.

    Args:
        db (Session): Database session.
        session_id (int): The ID of the session.
        user_id (int): The ID of the user.

    Returns:
        None
    """
    from datetime import datetime, timezone

    participant = (
        db.query(Participant)
        .filter(Participant.session_id == session_id, Participant.user_id == user_id)
        .first()
    )
    if participant:
        participant.left_at = datetime.now(timezone.utc)
        participant.is_connected = False
        db.commit()


def list_by_session(db: Session, session_id: int) -> list[Participant]:
    """Retrieve all participants for a specific session.

    Args:
        db (Session): Database session.
        session_id (int): The ID of the session.

    Returns:
        list[Participant]: A list of participant objects.
    """
    return db.query(Participant).filter(Participant.session_id == session_id).all()
