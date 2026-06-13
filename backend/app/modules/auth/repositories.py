"""
Database access for Users.
"""

from sqlalchemy.orm import Session
from app.modules.auth.models import User


def get_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by their email address.

    Args:
        db (Session): Database session.
        email (str): The email address to search for.

    Returns:
        User | None: The user if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session, email: str, password_hash: str, role: str, name: str = None
) -> User:
    """Create a new user in the database.

    Args:
        db (Session): Database session.
        email (str): The email address for the user.
        password_hash (str): The hashed password.
        role (str): The assigned role (e.g., 'agent', 'admin').
        name (str, optional): The user's name. Defaults to None.

    Returns:
        User: The created user object.
    """
    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_id(db: Session, user_id: int) -> User | None:
    """Retrieve a user by their ID.

    Args:
        db (Session): Database session.
        user_id (int): The unique ID of the user.

    Returns:
        User | None: The user if found, otherwise None.
    """
    return db.query(User).filter(User.id == user_id).first()
