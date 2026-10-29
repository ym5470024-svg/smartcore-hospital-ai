from __future__ import annotations

from typing import Any


def generate_insights(records: list[dict[str, Any]], question: str | None = None) -> list[str]:
    if not records:
        return ["No hospital records are available in the selected dataset."]
    insights = []
    highest = max(records, key=lambda r: (r.get("occupied_beds") or 0) / (r.get("total_beds") or 1)) if records else None
    if highest:
        rate = (highest.get("occupied_beds") or 0) / (highest.get("total_beds") or 1) * 100
        insights.append(
            f"{highest.get('hospital_name')} has a reported occupancy rate of {rate:.1f}% in the selected reporting period."
        )
    high_pressure = sum(1 for r in records if (r.get("occupied_beds") or 0) >= (r.get("total_beds") or 1) * 0.8)
    if high_pressure:
        insights.append(f"{high_pressure} hospitals are reported above the configured operational occupancy threshold.")
    if question:
        insights.append(f"Question addressed: {question}")
    return insights
