from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

ALIAS_MAP = {
    "hospital_id": ["hospital_id", "id", "facility_id", "hospital code", "رمز المستشفى"],
    "hospital_name": ["hospital_name", "hospital name", "name", "اسم المستشفى", "اسم المستشفي"],
    "governorate": ["governorate", "province", "المحافظة"],
    "city": ["city", "مدينة", "المدينة"],
    "district": ["district", "area", "الحي", "المنطقة"],
    "address": ["address", "location", "العنوان"],
    "latitude": ["latitude", "lat", "خط العرض"],
    "longitude": ["longitude", "lng", "lon", "خط الطول"],
    "hospital_type": ["hospital_type", "facility_type", "نوع المستشفى", "نوع المؤسسة"],
    "reporting_timestamp": ["reporting_timestamp", "last_updated", "updated_at", "last update", "آخر تحديث"],
    "reporting_period": ["reporting_period", "reporting_date", "period", "الفترة"],
    "total_beds": ["total_beds", "number_of_beds", "total beds", "عدد الأسرة", "إجمالي الأسرة"],
    "occupied_beds": ["occupied_beds", "occupied", "beds_occupied", "الأسرة المشغولة"],
    "available_beds": ["available_beds", "beds_available", "الأسرة المتاحة"],
    "emergency_capacity": ["emergency_capacity", "emergency beds", "قدرة الطوارئ"],
    "emergency_current_load": ["emergency_current_load", "emergency_load", "حمل الطوارئ"],
    "emergency_status": ["emergency_status", "emergency", "حالة الطوارئ"],
    "accident_service_available": ["accident_service_available", "accident_service", "خدمة الحوادث"],
    "burn_unit_available": ["burn_unit_available", "burn_unit", "حروق"],
    "intensive_care_available": ["intensive_care_available", "icu", "العناية المركزة"],
    "operating_room_available": ["operating_room_available", "or_available", "غرف العمليات"],
    "laboratory_available": ["laboratory_available", "lab_available", "المعمل"],
    "radiology_available": ["radiology_available", "radiology", "الأشعة"],
    "ambulance_service_available": ["ambulance_service_available", "ambulance", "الاسعاف"],
    "waiting_patients": ["waiting_patients", "waiting", "عدد المنتظرين"],
    "average_waiting_time_minutes": ["average_waiting_time_minutes", "wait_time_minutes", "متوسط الانتظار"],
    "staff_available": ["staff_available", "available_staff", "العاملين"],
    "source_name": ["source_name", "source", "مصدر البيانات"],
    "source_url": ["source_url", "url", "رابط المصدر"],
    "source_updated_at": ["source_updated_at", "source_updated", "تاريخ تحديث المصدر"],
    "data_quality_status": ["data_quality_status", "quality_status", "حالة الجودة"],
}


def normalize_header(header: str) -> str:
    if header is None:
        return ""
    value = str(header).strip().lower().replace("-", " ").replace("/", " ")
    value = "".join(ch for ch in value if ch.isalnum() or ch.isspace())
    value = " ".join(value.split())
    return value


def map_columns(columns: list[str]) -> dict[str, str]:
    normalized = {normalize_header(col): col for col in columns}
    mapping: dict[str, str] = {}
    for standard_name, aliases in ALIAS_MAP.items():
        for alias in aliases:
            normalized_alias = normalize_header(alias)
            if normalized_alias in normalized:
                mapping[standard_name] = normalized[normalized_alias]
                break
    return mapping


def read_uploaded_file(file_obj, file_name: str) -> pd.DataFrame:
    path = Path(file_name).suffix.lower()
    if path in {".csv"}:
        return pd.read_csv(file_obj)
    if path in {".xlsx", ".xls"}:
        return pd.read_excel(file_obj)
    raise ValueError("Unsupported file type. Upload a CSV or Excel file.")


def to_float(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace(" ", "")
        if cleaned in {"", "-", "N/A", "NaN", "None"}:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_str(value):
    if pd.isna(value):
        return None
    return str(value).strip() or None


def detect_duplicates(df: pd.DataFrame) -> list[int]:
    idx = []
    seen = set()
    for i, row in df.iterrows():
        key = (
            safe_str(row.get("hospital_id")) or safe_str(row.get("hospital_name")),
            safe_str(row.get("reporting_period")) or safe_str(row.get("reporting_timestamp")),
        )
        if key in seen:
            idx.append(i)
        else:
            seen.add(key)
    return idx


def validate_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    df = df.copy()
    warnings = []
    issue_rows = []
    mapped = map_columns(df.columns.tolist())
    for standard, original in mapped.items():
        if standard not in df.columns:
            df[standard] = df[original]
    for idx, row in df.iterrows():
        total = to_float(row.get("total_beds"))
        occupied = to_float(row.get("occupied_beds"))
        available = to_float(row.get("available_beds"))
        if total is not None and total < 0:
            issue_rows.append(f"Row {idx}: total_beds is negative.")
        if occupied is not None and total is not None and occupied > total:
            issue_rows.append(f"Row {idx}: occupied_beds exceeds total_beds.")
        if total is not None and occupied is not None:
            derived = total - occupied
            if available is not None and abs(available - derived) > 1:
                issue_rows.append(f"Row {idx}: available_beds differs from total_beds - occupied_beds.")
        if row.get("latitude") is not None and (row.get("latitude") < -90 or row.get("latitude") > 90):
            issue_rows.append(f"Row {idx}: latitude is out of range.")
        if row.get("longitude") is not None and (row.get("longitude") < -180 or row.get("longitude") > 180):
            issue_rows.append(f"Row {idx}: longitude is out of range.")
    dup_indices = detect_duplicates(df)
    for d in dup_indices:
        warnings.append(f"Duplicate hospital-period record found at row {d}.")
    return df, warnings, issue_rows
