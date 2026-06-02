from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.database import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True, index=True)

    provider = Column(String(100), nullable=False)

    rows_read = Column(Integer, nullable=False)
    rows_valid = Column(Integer, nullable=False)
    rows_rejected = Column(Integer, nullable=False)

    rows_inserted = Column(Integer, nullable=False)
    rows_skipped_existing = Column(Integer, nullable=False)

    elapsed_seconds = Column(Float, nullable=False)

    status = Column(String(20), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    