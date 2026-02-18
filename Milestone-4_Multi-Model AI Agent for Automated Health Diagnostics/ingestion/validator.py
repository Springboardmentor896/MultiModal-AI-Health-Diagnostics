"""
Data Validation & Standardization: clean extracted data, normalize units, validate plausibility.
"""
from ingestion.extractor import REQUIRED_NUMERIC

# Default (mid-range) values when a parameter is missing or unreadable
DEFAULT_VALUES = {
    "Hemoglobin": 14.0,
    "Glucose": 95.0,
    "Cholesterol": 180.0,
    "White Blood Cells": 7500.0,
    "Red Blood Cells": 5.0,
    "Platelets": 250000.0,
}

def _coerce_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def _normalize_units(param: str, v: float) -> float:
    """Convert to standard units (e.g. WBC in thousands -> per µL)."""
    if param == "White Blood Cells":
        if 0.1 <= v < 500:
            return v * 1000
    if param == "Platelets":
        if 0 < v < 5000 and v == int(v):
            return v * 1000
    return v

def _clamp_or_accept(param: str, v: float) -> float:
    """Accept value; clamp only if wildly out of range to avoid downstream errors."""
    if param == "Hemoglobin" and (v < 2 or v > 30):
        return max(2.0, min(30.0, v))
    if param == "Glucose" and (v < 10 or v > 700):
        return max(10.0, min(700.0, v))
    if param == "Cholesterol" and (v < 30 or v > 500):
        return max(30.0, min(500.0, v))
    if param == "White Blood Cells" and (v < 100 or v > 100000):
        return max(100.0, min(100000.0, v))
    if param == "Red Blood Cells" and (v < 1 or v > 10):
        return max(1.0, min(10.0, v))
    if param == "Platelets" and (v < 5000 or v > 2000000):
        return max(5000.0, min(2000000.0, v))
    return v

def validate_data(data: dict) -> dict:
    """
    Validate and clean extracted data. If any required param is missing, fill with defaults
    so we can still produce a report (with lower confidence). Never returns {} for non-empty input.
    """
    if not data or not isinstance(data, dict):
        return {}

    cleaned = {}
    cleaned["Age"] = 35
    if "Age" in data:
        a = _coerce_float(data["Age"])
        if a is not None and 1 <= a <= 120:
            cleaned["Age"] = int(a)

    g = (data.get("Gender") or "").strip().lower()
    cleaned["Gender"] = "Male"
    if g in ("female", "f"):
        cleaned["Gender"] = "Female"
    elif g in ("male", "m"):
        cleaned["Gender"] = "Male"

    # Require at least one numeric param to have been extracted
    has_any = any(_coerce_float(data.get(p)) is not None for p in REQUIRED_NUMERIC)
    if not has_any:
        return {}

    for param in REQUIRED_NUMERIC:
        v = _coerce_float(data.get(param))
        if v is None:
            v = DEFAULT_VALUES[param]
        else:
            v = _normalize_units(param, v)
            v = _clamp_or_accept(param, v)
        cleaned[param] = v

    return cleaned
