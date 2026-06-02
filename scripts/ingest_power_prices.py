import argparse
import time
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy.dialects.postgresql import insert

from app.database import Base, SessionLocal, engine
from app.models.power_price import PowerPrice
from app.services.validator import clean_power_prices, validate_power_prices
from app.models.ingestion_run import IngestionRun


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ingest_power_prices(config_path: str) -> dict:
    started_at = time.perf_counter()
    config = load_config(config_path)
    source_file = Path(config["source_file"])

    Base.metadata.create_all(bind=engine)

    df = pd.read_csv(source_file)
    df = clean_power_prices(df)
    validation = validate_power_prices(df, config)

    if not validation.is_valid:
        raise ValueError(f"Validation failed: {validation.errors}")

    records = df.to_dict(orient="records")
    rows_inserted = 0

    with SessionLocal() as db:
        for record in records:
            statement = insert(PowerPrice).values(**record)
            statement = statement.on_conflict_do_nothing(
                index_elements=["trade_date", "country"]
            )
            result = db.execute(statement)
            rows_inserted += result.rowcount or 0
        db.commit()

    elapsed_seconds = round(time.perf_counter() - started_at, 4)
    rows_skipped = validation.rows_valid - rows_inserted

    metrics = {
        "source_file": str(source_file),
        "rows_read": validation.rows_read,
        "rows_valid": validation.rows_valid,
        "rows_rejected": validation.rows_rejected,
        "rows_inserted": rows_inserted,
        "rows_skipped_existing": rows_skipped,
        "elapsed_seconds": elapsed_seconds,
    }

    with SessionLocal() as db:
        db.add(
            IngestionRun(
                provider=config.get("provider", "UNKNOWN"),
                rows_read=validation.rows_read,
                rows_valid=validation.rows_valid,
                rows_rejected=validation.rows_rejected,
                rows_inserted=rows_inserted,
                rows_skipped_existing=rows_skipped,
                elapsed_seconds=elapsed_seconds,
                status="SUCCESS",
            )
        )
        db.commit()

    print(metrics)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest power price data into Postgres.")
    parser.add_argument(
        "--config",
        default="configs/power_prices.yaml",
        help="Path to provider configuration YAML file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ingest_power_prices(args.config)
