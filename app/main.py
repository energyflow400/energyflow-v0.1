from fastapi import FastAPI

from app.api.prices import router as prices_router
from app.database import Base, engine
from app.models.ingestion_run import IngestionRun
from app.api.ingestion_runs import router as ingestion_runs_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EnergyFlow API",
    description="Cost-aware v0.1 market data pipeline demo: CSV ingestion, validation, Postgres storage, and FastAPI access.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(prices_router)
app.include_router(ingestion_runs_router)
