from __future__ import annotations

from typing import Any

import numpy as np


def forecast_series(values: list[float], horizon: int = 1) -> dict[str, Any]:
    if len(values) < 3:
        return {
            "status": "Insufficient historical data",
            "forecast": None,
            "method": "Simple moving average",
        }
    arr = np.asarray(values, dtype=float)
    recent_mean = float(np.mean(arr[-3:]))
    forecast_value = float(recent_mean)
    return {
        "status": "Forecast generated",
        "forecast": round(forecast_value, 2),
        "method": "Simple moving average",
        "horizon": horizon,
        "basis": "Last three observations",
    }


def validate_forecast_requirements(history: list[float]) -> bool:
    return len(history) >= 3
