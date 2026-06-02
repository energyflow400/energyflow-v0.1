# EnergyFlow v0.1

A lightweight, cost-aware data engineering prototype for market data ingestion.

The goal is to demonstrate a simple pattern:

```text
CSV/provider data
  -> validation
  -> incremental Postgres load
  -> FastAPI access layer
```

## Why this exists

This prototype mirrors a small slice of a larger data engineering platform:

- ingest external provider-style data
- validate quality before loading
- avoid duplicate processing
- store data in Postgres
- expose data through API endpoints
- run the API and database with Docker Compose

## Architecture

```text
Provider Data (CSV/API)
          │
          ▼
     Validation
          │
          ▼
 Incremental Load
          │
          ▼
      Postgres
      ├──────────────┐
      ▼              ▼
 Power Prices   Ingestion Runs
      │              │
      └──────┬───────┘
             ▼
          FastAPI
             │
             ▼
      API Consumers
```

## Cost-aware Choices in v0.1

- `UNIQUE(trade_date, country)` prevents duplicate loads.
- Incremental loading avoids reprocessing existing records.
- `INDEX(country, trade_date)` supports common query paths.
- API endpoints use `LIMIT` to avoid returning entire tables.
- Docker uses `python:3.11-slim` for a smaller image.
- Ingestion logs operational metrics including rows read, inserted, skipped, rejected, runtime, and execution status.

## Run Locally

Start the application:

```bash
docker compose up --build
```

In another terminal, load the default provider dataset:

```bash
docker compose exec api python -m scripts.ingest_power_prices --config configs/power_prices.yaml
```

Verify incremental loading:

```bash
docker compose exec api python -m scripts.ingest_power_prices
```

Expected behaviour:

- First run inserts new records.
- Subsequent runs skip existing records.
- No duplicate rows are created.

Open API docs:

```text
http://localhost:8000/docs
```

## Multiple Provider Example

The ingestion framework supports provider-specific configuration files.

Load Provider A:

```bash
docker compose exec api python -m scripts.ingest_power_prices --config configs/power_prices.yaml
```

Load Provider B:

```bash
docker compose exec api python -m scripts.ingest_power_prices --config configs/power_prices_provider_b.yaml
```

Expected behaviour:

- Both providers use the same ingestion and validation logic.
- Provider-specific settings are stored in configuration files.
- Existing records are skipped automatically.
- Only new records are inserted.

## Operational Visibility

Each ingestion run is recorded in the `ingestion_runs` table.

Captured metrics include:

- provider
- rows read
- rows validated
- rows rejected
- rows inserted
- rows skipped
- runtime
- execution status
- timestamp

This provides a foundation for:

- monitoring
- cost optimization
- auditing
- operational reporting
- pipeline performance analysis

Example endpoint:

```text
GET /ingestion-runs
```

Example response:

```json
[
  {
    "provider": "PROVIDER_A",
    "rows_read": 7,
    "rows_inserted": 0,
    "rows_skipped_existing": 7,
    "elapsed_seconds": 0.1274,
    "status": "SUCCESS"
  }
]
```

## Endpoints

```text
GET /health
GET /prices
GET /prices/latest
GET /prices/country/{country}
GET /ingestion-runs
```

Examples:

```text
http://localhost:8000/prices
http://localhost:8000/prices/latest
http://localhost:8000/prices/country/CZ
http://localhost:8000/ingestion-runs
```

## Future Extensions

- Replace CSV with real provider API ingestion.
- Add Airflow DAG orchestration.
- Generalize provider configs into reusable Airflow DAG templates.
- Add validation reports and alerting.
- Add environment-specific deployment settings.
- Add data quality monitoring dashboards.
- Add ingestion performance and cost reporting.
- Integrate cloud-native scheduling and orchestration.

## Key Design Principles

- Keep ingestion logic reusable and provider-agnostic.
- Separate configuration from implementation.
- Validate data before loading.
- Minimize unnecessary processing and database writes.
- Build simple patterns that can scale to larger orchestration frameworks.
- Favor maintainability and operational visibility over premature complexity.
- Design for observability from the beginning.
- Optimize for incremental processing and operational efficiency.