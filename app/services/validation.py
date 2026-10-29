from __future__ import annotations

import pandas as pd

from app.schemas import detect_duplicates, to_float, validate_dataframe


def validate_uploaded_dataframe(df: pd.DataFrame):
    cleaned, warnings, issue_rows = validate_dataframe(df)
    return cleaned, warnings, issue_rows


def preview_upload(file_obj, file_name: str):
    if str(file_name).lower().endswith(".csv"):
        df = pd.read_csv(file_obj)
    else:
        df = pd.read_excel(file_obj)
    cleaned, warnings, issue_rows = validate_uploaded_dataframe(df)
    return {
        "columns": list(cleaned.columns),
        "preview_rows": cleaned.head(10).to_dict(orient="records"),
        "warnings": warnings + issue_rows,
        "file_name": file_name,
    }


def build_clean_record(raw_row: dict) -> dict:
    record = {}
    for key, value in raw_row.items():
        if not pd.isna(value):
            if key in {"total_beds", "occupied_beds", "available_beds", "emergency_capacity", "emergency_current_load", "waiting_patients", "average_waiting_time_minutes", "staff_available", "latitude", "longitude"}:
                numeric = to_float(value)
                record[key] = numeric
            else:
                record[key] = str(value).strip()
    return record


def detect_duplicate_rows(df: pd.DataFrame):
    return detect_duplicates(df)
