from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modules.websocket.manager import manager

from .services import update_gauges

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_class=PlainTextResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Serve Prometheus metrics.

    Updates the dynamic gauges with the latest real-time metrics
    before fetching the generated report for Prometheus.

    Args:
        db (Session): Database session dependency.

    Returns:
        PlainTextResponse: The Prometheus metrics data in plain text.
    """
    # Update dynamic gauges before generating the report
    try:
        update_gauges(db, manager)
    except Exception:
        pass

    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
