"""
Business logic for Participants.
"""

import uuid

import structlog
from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.core.livekit import get_livekit
from app.modules.auth import repositories as auth_repos
from app.modules.participants import repositories as participant_repos
from app.modules.sessions import repositories as session_repos

logger = structlog.get_logger()


def join_session(db: DbSession, join_token: str, name: str):
    """Process a customer joining via a token.

    Validates token, creates ephemeral customer User, creates Participant record,
    and generates a LiveKit token.

    Args:
        db (DbSession): Database session.
        join_token (str): The unique token for joining the session.
        name (str): The display name chosen by the customer.

    Returns:
        dict: A dictionary containing livekit_token, room_name, identity, session_id,
              backend_token, and user_id.

    Raises:
        HTTPException: If the token is invalid, expired, or the session is inactive.
    """
    session = session_repos.get_session_by_token(db, join_token)
    if not session:
        logger.warning("join_failed_invalid_token", token=join_token)
        raise HTTPException(status_code=404, detail="Invalid or expired join link")

    if session.status != "waiting" and session.status != "active":
        logger.warning(
            "join_failed_invalid_status", session_id=session.id, status=session.status
        )
        raise HTTPException(status_code=400, detail="Session is no longer active")

    # Create ephemeral user
    # Note: password is a random uuid, as ephemeral users don't log in directly
    ephemeral_email = f"guest-{uuid.uuid4().hex[:8]}@ephemeral.local"
    ephemeral_user = auth_repos.create_user(
        db=db, email=ephemeral_email, password_hash=uuid.uuid4().hex, role="customer"
    )

    # Create participant
    identity = f"customer-{uuid.uuid4().hex[:8]}"
    participant_repos.create_participant(
        db=db,
        session_id=session.id,
        user_id=ephemeral_user.id,
        identity=identity,
        name=name,
    )

    # Generate LiveKit Token
    livekit = get_livekit()
    token = livekit.generate_token(
        identity=identity,
        room_name=session.room_name,
        name=name,
        can_publish=True,
        can_subscribe=True,
    )

    # Generate Backend Token for the ephemeral user
    from app.modules.auth.services import create_access_token

    access_token = create_access_token(
        data={"sub": str(ephemeral_user.id), "role": ephemeral_user.role}
    )

    logger.info(
        "customer_joined_session",
        session_id=session.id,
        identity=identity,
        user_id=ephemeral_user.id,
    )

    return {
        "livekit_token": token,
        "room_name": session.room_name,
        "identity": identity,
        "session_id": session.id,
        "backend_token": access_token,
        "user_id": ephemeral_user.id,
    }


def join_as_agent(db: DbSession, session_id: int, agent_id: int, name: str):
    """Process an agent joining their session.

    Args:
        db (DbSession): Database session.
        session_id (int): The ID of the session.
        agent_id (int): The ID of the agent attempting to join.
        name (str): The display name of the agent.

    Returns:
        dict: A dictionary with the livekit_token, room_name, identity, and session_id.

    Raises:
        HTTPException: If the session is missing or the agent is not authorized.
    """
    session = session_repos.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.agent_id != agent_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to join this session"
        )

    identity = f"agent-{agent_id}"

    # Upsert participant logic for agent
    participant = participant_repos.get_by_identity(db, identity)
    if not participant:
        participant_repos.create_participant(
            db=db, session_id=session.id, user_id=agent_id, identity=identity, name=name
        )

    # Mark session as active if it was waiting
    if session.status == "waiting":
        session.status = "active"
        db.commit()

    livekit = get_livekit()
    token = livekit.generate_token(
        identity=identity,
        room_name=session.room_name,
        name=name,
        can_publish=True,
        can_subscribe=True,
    )

    logger.info("agent_joined_session", session_id=session.id, agent_id=agent_id)

    return {
        "livekit_token": token,
        "room_name": session.room_name,
        "identity": identity,
        "session_id": session.id,
    }
