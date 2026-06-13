"""
Database seed script.
Creates initial admin and test agent users on first run.
Admin-only registration — agents are created by admin.
"""

import structlog
from sqlalchemy.orm import Session

from app.core.security import hash_password

logger = structlog.get_logger()

# Default seed users
SEED_USERS = [
    {
        "email": "admin@atomquest.com",
        "password": "admin123",
        "role": "admin",
    },
    {
        "email": "agent@atomquest.com",
        "password": "agent123",
        "role": "agent",
    },
    {
        "email": "john.doe@atomquest.com",
        "password": "password123",
        "role": "agent",
    },
    {
        "email": "jane.smith@atomquest.com",
        "password": "password123",
        "role": "agent",
    },
]


# def _ensure_name_column(db: Session) -> None:
#     """Add name column to users table if it doesn't exist (safe migration)."""
#     from sqlalchemy import text
#     try:
#         db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR"))
#         db.commit()
#         logger.info("migration_name_column_ok")
#     except Exception as e:
#         db.rollback()
#         logger.warning("migration_name_column_skipped", error=str(e))


def seed_users(db: Session) -> None:
    """Seed default users if they don't already exist.

    Args:
        db (Session): Database session to use for seeding.

    Returns:
        None
    """

    # Import here to avoid circular imports at module level
    from app.modules.auth.models import User

    for user_data in SEED_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            logger.info("seed_user_exists", email=user_data["email"])
            continue

        user = User(
            email=user_data["email"],
            name=user_data.get("name"),
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"],
        )
        db.add(user)
        logger.info(
            "seed_user_created",
            email=user_data["email"],
            role=user_data["role"],
        )

    db.commit()
    logger.info("seed_complete")


def run_seed() -> None:
    """Run the seed script using a fresh database session.

    Returns:
        None
    """
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
