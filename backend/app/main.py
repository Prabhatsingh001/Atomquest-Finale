"""
AtomQuest Backend - FastAPI Application Factory
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import uuid
import time

from app.core.config import settings
from app.logging_config import setup_logging
from app.db.seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Yields control back to the FastAPI framework.
    """
    setup_logging()
    logger = structlog.get_logger()
    logger.info("AtomQuest backend starting up")

    import os

    os.makedirs("/app/recordings", exist_ok=True)
    os.chmod("/app/recordings", 0o777)

    from app.core.celery_app import celery_app

    celery_app.set_default()

    # Run database seed
    run_seed()

    yield
    logger.info("AtomQuest backend shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(
        title="AtomQuest API",
        description="Real-Time Video Support Platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging and Metrics Middleware
    # Paths to skip logging for (high-frequency or noisy)
    QUIET_PATHS = {"/api/health", "/api/metrics", "/api/ws"}

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Middleware to log HTTP requests and capture metrics.

        Args:
            request (Request): The incoming HTTP request.
            call_next (callable): The next middleware or route handler.

        Returns:
            Response: The HTTP response from the application.

        Raises:
            Exception: Re-raises any exception that occurs during request handling.
        """
        path = request.url.path

        # Skip verbose logging for noisy endpoints
        if any(path.startswith(p) for p in QUIET_PATHS):
            return await call_next(request)

        structlog.contextvars.clear_contextvars()
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(
            request_id=request_id, method=request.method, path=path
        )
        start_time = time.time()
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            try:
                from app.modules.metrics.services import ERRORS_TOTAL

                ERRORS_TOTAL.inc()
            except Exception:
                pass
            structlog.get_logger().error("request_failed", exc_info=True)
            raise e
        finally:
            process_time = time.time() - start_time
            # Only log slow requests (>1s) or errors to keep output clean
            if process_time > 1.0:
                structlog.get_logger().warning(
                    "slow_request", duration=round(process_time, 3)
                )

    # Health check
    @app.get("/api/health", tags=["Health"])
    async def health_check():
        """Health check endpoint to monitor application status.

        Returns:
            dict: A dictionary containing the status and service name.
        """
        return {"status": "healthy", "service": "atomquest-backend"}

    # Register routers
    from app.modules.auth.routes import router as auth_router
    from app.modules.sessions.routes import router as sessions_router
    from app.modules.participants.routes import router as participants_router
    from app.modules.chat.routes import router as chat_router
    from app.modules.websocket.routes import router as websocket_router
    from app.modules.recordings.routes import router as recordings_router
    from app.modules.admin.routes import router as admin_router
    from app.modules.uploads.routes import router as uploads_router
    from app.modules.metrics.routes import router as metrics_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(sessions_router, prefix="/api/sessions", tags=["Sessions"])
    app.include_router(
        participants_router, prefix="/api/participants", tags=["Participants"]
    )
    app.include_router(chat_router, prefix="/api", tags=["Chat"])
    app.include_router(websocket_router, prefix="/api", tags=["WebSocket"])
    app.include_router(recordings_router, prefix="/api", tags=["Recordings"])
    app.include_router(admin_router, prefix="/api", tags=["Admin"])
    app.include_router(uploads_router, prefix="/api", tags=["Uploads"])
    app.include_router(metrics_router, prefix="/api", tags=["Metrics"])

    return app


app = create_app()
