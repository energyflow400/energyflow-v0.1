from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ingestion_run import IngestionRun

router = APIRouter(prefix="/ingestion-runs", tags=["ingestion-runs"])


@router.get("")
def list_ingestion_runs(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    runs = (
        db.query(IngestionRun)
        .order_by(IngestionRun.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": run.id,
            "provider": run.provider,
            "rows_read": run.rows_read,
            "rows_valid": run.rows_valid,
            "rows_rejected": run.rows_rejected,
            "rows_inserted": run.rows_inserted,
            "rows_skipped_existing": run.rows_skipped_existing,
            "elapsed_seconds": run.elapsed_seconds,
            "status": run.status,
            "created_at": run.created_at,
        }
        for run in runs
    ]
