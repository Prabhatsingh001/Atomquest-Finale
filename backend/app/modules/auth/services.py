"""
Business logic for authentication.
"""

import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth import repositories

logger = structlog.get_logger()


def signup(db: Session, name: str, email: str, password: str):
    """Register a new agent.

    Args:
        db (Session): Database session.
        name (str): The name of the agent.
        email (str): The email address for the account.
        password (str): The plaintext password.

    Returns:
        User: The newly created user.

    Raises:
        HTTPException: If the email is already registered.
    """
    existing_user = repositories.get_by_email(db, email)
    if existing_user:
        logger.warning("signup_failed_email_exists", email=email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(password)
    user = repositories.create_user(db, email, hashed_password, role="agent", name=name)
    logger.info("signup_success", user_id=user.id, email=email)
    return user


def authenticate(db: Session, email: str, password: str):
    """Authenticate a user and return the user object.

    Args:
        db (Session): Database session.
        email (str): The login email address.
        password (str): The plaintext password.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the email is not found or the password incorrect.
    """
    user = repositories.get_by_email(db, email)
    if not user:
        logger.warning("auth_failed_user_not_found", email=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(password, user.password_hash):
        logger.warning("auth_failed_invalid_password", email=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    logger.info("auth_success", user_id=user.id, email=email, role=user.role)
    return user


def generate_login_response(user) -> dict:
    """Generate the JWT token and login response payload.

    Args:
        user (User): The authenticated user object.

    Returns:
        dict: A dictionary containing the access token, token type, and user data.
    """
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
