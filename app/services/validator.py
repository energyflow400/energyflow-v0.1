from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    rows_read: int
    rows_valid: int
    rows_rejected: int


def validate_power_prices(df: pd.DataFrame, config: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    rows_read = len(df)

    required_columns = config.get("required_columns", [])
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
        return ValidationResult(False, errors, rows_read, 0, rows_read)

    clean_df = df.copy()
    clean_df["trade_date"] = pd.to_datetime(clean_df["trade_date"], errors="coerce").dt.date
    clean_df["power_price_eur_mwh"] = pd.to_numeric(clean_df["power_price_eur_mwh"], errors="coerce")

    null_rows = clean_df[required_columns].isna().any(axis=1)
    if null_rows.any():
        errors.append(f"Rows with null or invalid required values: {int(null_rows.sum())}")

    allowed_countries = set(config.get("country_codes", []))
    invalid_country_rows = ~clean_df["country"].isin(allowed_countries)
    if invalid_country_rows.any():
        errors.append(f"Rows with unsupported country codes: {int(invalid_country_rows.sum())}")

    allow_negative = config.get("validation", {}).get("allow_negative_prices", False)
    negative_price_rows = clean_df["power_price_eur_mwh"] < 0
    if negative_price_rows.any() and not allow_negative:
        errors.append(f"Rows with negative prices: {int(negative_price_rows.sum())}")

    unique_key = config.get("validation", {}).get("unique_key", ["trade_date", "country"])
    duplicate_rows = clean_df.duplicated(subset=unique_key, keep="first")
    if duplicate_rows.any():
        errors.append(f"Duplicate rows in input file based on {unique_key}: {int(duplicate_rows.sum())}")

    invalid_mask = null_rows | invalid_country_rows | duplicate_rows
    if not allow_negative:
        invalid_mask = invalid_mask | negative_price_rows

    rows_rejected = int(invalid_mask.sum())
    rows_valid = rows_read - rows_rejected

    return ValidationResult(rows_rejected == 0, errors, rows_read, rows_valid, rows_rejected)


def clean_power_prices(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    clean_df["trade_date"] = pd.to_datetime(clean_df["trade_date"], errors="coerce").dt.date
    clean_df["power_price_eur_mwh"] = pd.to_numeric(clean_df["power_price_eur_mwh"], errors="coerce")
    clean_df["country"] = clean_df["country"].str.upper().str.strip()
    clean_df["source"] = clean_df["source"].str.strip()
    return clean_df
