from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.validation import validate_uploaded_dataframe


def preview_upload(file_obj, file_name: str) -> dict[str, Any]:
    df = pd.read_csv(file_obj) if str(file_name).lower().endswith(".csv") else pd.read_excel(file_obj)
    cleaned, warnings, issue_rows = validate_uploaded_dataframe(df)
    records = cleaned.head(10).to_dict(orient="records")
    return {
        "columns": list(cleaned.columns),
        "preview_rows": records,
        "warnings": warnings + issue_rows,
        "file_name": file_name,
    }


def parse_and_validate(file_obj, file_name: str) -> tuple[pd.DataFrame, list[str], list[str]]:
    if str(file_name).lower().endswith(".csv"):
        df = pd.read_csv(file_obj)
    elif str(file_name).lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_obj)
    else:
        raise ValueError("Unsupported file type.")
    return validate_uploaded_dataframe(df)
