from __future__ import annotations

import math
from typing import Any

from app.schemas import to_float


def occupancy_rate(occupied: float | None, total: float | None) -> float | None:
    if occupied is None or total in (None, 0):
        return None
    return round((occupied / total) * 100.0, 2)


def available_capacity(total: float | None, occupied: float | None) -> float | None:
    if total is None or occupied is None:
        return None
    return round(max(total - occupied, 0.0), 2)


def compute_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    clean_records = [r for r in records if r.get("hospital_name")]
    total_hospitals = len(clean_records)
    recent = [r for r in clean_records if r.get("reporting_timestamp")]
    occupancy_values = [occupancy_rate(r.get("occupied_beds"), r.get("total_beds")) for r in clean_records]
    valid_occupancies = [v for v in occupancy_values if v is not None]
    avg_occupancy = round(sum(valid_occupancies) / len(valid_occupancies), 2) if valid_occupancies else None
    high_pressure = sum(1 for r in clean_records if occupancy_rate(r.get("occupied_beds"), r.get("total_beds")) is not None and occupancy_rate(r.get("occupied_beds"), r.get("total_beds")) >= 80)
    return {
        "total_hospitals": total_hospitals,
        "recent_reports": len(recent),
        "average_occupancy": avg_occupancy,
        "high_pressure_hospitals": high_pressure,
    }


def compute_crowding(records: list[dict[str, Any]], threshold: float = 75.0) -> dict[str, Any]:
    flagged = []
    for record in records:
        rate = occupancy_rate(record.get("occupied_beds"), record.get("total_beds"))
        if rate is not None and rate >= threshold:
            flagged.append({
                "hospital_name": record.get("hospital_name"),
                "occupancy_rate": rate,
                "reporting_period": record.get("reporting_period"),
            })
    return {"threshold": threshold, "flagged_hospitals": flagged}


def compute_service_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    service_columns = [
        "accident_service_available",
        "burn_unit_available",
        "intensive_care_available",
        "operating_room_available",
        "laboratory_available",
        "radiology_available",
        "ambulance_service_available",
    ]
    summary: dict[str, dict[str, int]] = {}
    for col in service_columns:
        summary[col] = {"available": 0, "unavailable": 0, "unknown": 0}
        for record in records:
            value = str(record.get(col, "")).strip().lower()
            if value in {"available", "yes", "true", "1"}:
                summary[col]["available"] += 1
            elif value in {"unavailable", "no", "false", "0"}:
                summary[col]["unavailable"] += 1
            else:
                summary[col]["unknown"] += 1
    return summary


def compute_trend(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(records, key=lambda r: r.get("reporting_period") or "")
    rows = []
    for record in ordered:
        rate = occupancy_rate(record.get("occupied_beds"), record.get("total_beds"))
        rows.append({
            "hospital_name": record.get("hospital_name"),
            "reporting_period": record.get("reporting_period"),
            "occupancy_rate": rate,
        })
    return rows
