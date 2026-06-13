"""
Auth API endpoints.
"""

import fastapi
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import get_current_user
from app.db.database import get_db
from app.modules.auth import schemas, services
from app.modules.auth.models import User

router = APIRouter()


@router.post("/signup", response_model=schemas.LoginResponse)
def signup(request: schemas.SignupRequest, db: Session = Depends(get_db)):
    """Register a new agent and return JWT.

    Args:
        request (schemas.SignupRequest): The signup request containing name, email, and password.
        db (Session): Database session dependency.

    Returns:
        schemas.LoginResponse: The login response containing the auth token and user detials.
    """
    user = services.signup(db, request.name, request.email, request.password)
    return services.generate_login_response(user)


@router.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate agent/admin and return JWT.

    Args:
        request (schemas.LoginRequest): The login request containing email and password.
        db (Session): Database session dependency.

    Returns:
        schemas.LoginResponse: The login response containing the auth token and user details.
    """
    user = services.authenticate(db, request.email, request.password)
    return services.generate_login_response(user)


@router.post("/logout")
def logout(
    credentials: fastapi.security.HTTPAuthorizationCredentials = Depends(
        fastapi.security.HTTPBearer()
    ),
):
    """Revoke the current JWT and add it to the Redis blacklist.

    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials containing the JWT.

    Returns:
        dict: A status message indicating successful logout.
    """
    from datetime import datetime, timezone

    from app.core.security import decode_access_token
    from app.db.redis import redis_client

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload and "exp" in payload:
        # Calculate remaining time until expiration
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        ttl = int((exp_time - now).total_seconds())

        if ttl > 0:
            # Store in Redis with TTL so it auto-expires
            redis_client.setex(f"blacklist:{token}", ttl, "revoked")

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile.

    Args:
        current_user (User): The authenticated user dependency.

    Returns:
        User: The current user.
    """
    return current_user
