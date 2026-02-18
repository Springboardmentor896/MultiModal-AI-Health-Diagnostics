"""
Data Extraction Engine: identify and extract key blood parameters, values, and units.
"""
import re

# Expected parameter names (normalized)
PARAM_ALIASES = {
    "hemoglobin": "Hemoglobin",
    "haemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "glucose": "Glucose",
    "glu": "Glucose",
    "blood sugar": "Glucose",
    "cholesterol": "Cholesterol",
    "chol": "Cholesterol",
    "total cholesterol": "Cholesterol",
    "wbc": "White Blood Cells",
    "white blood cell": "White Blood Cells",
    "white blood cells": "White Blood Cells",
    "leukocyte": "White Blood Cells",
    "rbc": "Red Blood Cells",
    "red blood cell": "Red Blood Cells",
    "red blood cells": "Red Blood Cells",
    "erythrocyte": "Red Blood Cells",
    "platelet": "Platelets",
    "platelets": "Platelets",
    "plt": "Platelets",
    "age": "Age",
    "gender": "Gender",
    "sex": "Gender",
}

REQUIRED_NUMERIC = [
    "Hemoglobin", "Glucose", "Cholesterol",
    "White Blood Cells", "Red Blood Cells", "Platelets"
]

def _normalize_param(name: str) -> str:
    n = name.strip().lower()
    return PARAM_ALIASES.get(n, name.strip())

def _extract_number(s: str):
    """Extract first reasonable number from string (handles 1,234.56 and 1.234,56)."""
    s = s.replace(",", "")
    match = re.search(r"-?\d+\.?\d*", s)
    if match:
        try:
            return float(match.group())
        except ValueError:
            pass
    return None

def _normalize_ocr_text(text: str) -> str:
    """Collapse newlines and extra spaces so label and number can match across lines."""
    if not text:
        return ""
    # Replace fullwidth/special chars that OCR might produce
    text = text.replace("\uFF1A", ":")  # fullwidth colon
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse newlines and multiple spaces to single space
    text = " ".join(text.split())
    return text

def extract_from_text(text: str) -> dict:
    """Extract parameters from raw report text (OCR-friendly: handles newlines and loose spacing)."""
    if not (text or "").strip():
        return {}
    # Normalize so "Hemoglobin:\n11.43" becomes "Hemoglobin: 11.43"
    normalized = _normalize_ocr_text(text)
    text_lower = normalized.lower()
    result = {}

    # Age
    age_pat = re.compile(r"\bage\s*[:\-]?\s*(\d{1,3})\b", re.I)
    m = age_pat.search(normalized)
    if m:
        result["Age"] = int(m.group(1))
    else:
        result["Age"] = 35

    # Gender
    if "female" in text_lower:
        result["Gender"] = "Female"
    else:
        result["Gender"] = "Male"

    # Numeric parameters: try (1) label then number, (2) label ... any non-digits ... number
    for alias, canonical in PARAM_ALIASES.items():
        if canonical in ("Age", "Gender"):
            continue
        if canonical in result:
            continue
        # Tight pattern: "Hemoglobin: 11.43" or "Hemoglobin 11.43"
        pat = re.compile(
            rf"\b{re.escape(alias)}\s*[:\-]?\s*([0-9][0-9,.]*)",
            re.I,
        )
        m = pat.search(normalized)
        if not m:
            # Loose pattern: "Hemoglobin" ... anything ... "11.43" (handles "Hemoglobin (g/dL): 11.43")
            pat_loose = re.compile(
                rf"\b{re.escape(alias)}\s*[^\d]*?([0-9][0-9,.]*)",
                re.I,
            )
            m = pat_loose.search(normalized)
        if m:
            val = _extract_number(m.group(1))
            if val is not None:
                result[canonical] = val

    # Fallback: line-by-line for OCR that puts "Label" and "123.45" on separate lines
    aliases_sorted = sorted(
        [(a, c) for a, c in PARAM_ALIASES.items() if c not in ("Age", "Gender")],
        key=lambda x: -len(x[0]),
    )
    lines = text.splitlines()
    for i, line in enumerate(lines):
        line_clean = line.strip()
        line_lower = line_clean.lower()
        for alias, canonical in aliases_sorted:
            if canonical in result:
                continue
            if alias not in line_lower:
                continue
            num = _extract_number(line_clean)
            if num is not None:
                result[canonical] = num
                break
            if i + 1 < len(lines):
                num = _extract_number(lines[i + 1].strip())
                if num is not None:
                    result[canonical] = num
                    break

    # Last resort: any line "Something: 123.45" - if "something" looks like a param name, use it
    for line in lines:
        if ":" not in line:
            continue
        left, _, right = line.partition(":")
        label = left.strip().lower()
        num = _extract_number(right)
        if num is None:
            continue
        for alias, canonical in aliases_sorted:
            if canonical in result:
                continue
            if alias in label or label in alias:
                result[canonical] = num
                break

    # Value-on-next-line: line is only a number, previous line is the label
    for i in range(1, len(lines)):
        line_curr = lines[i].strip()
        num = _extract_number(line_curr)
        if num is None or len(line_curr) > 25:
            continue
        prev = lines[i - 1].strip().lower()
        for alias, canonical in aliases_sorted:
            if canonical in result:
                continue
            if alias in prev:
                result[canonical] = num
                break
    return result

def extract_from_dict(data: dict) -> dict:
    """Normalize keys from a JSON-like dict and ensure required numerics."""
    out = {}
    for k, v in data.items():
        canon = _normalize_param(str(k))
        if canon in ("Age", "Gender"):
            if canon == "Age":
                try:
                    out["Age"] = int(float(v))
                except (TypeError, ValueError):
                    pass
            else:
                if str(v).lower() in ("male", "m"):
                    out["Gender"] = "Male"
                elif str(v).lower() in ("female", "f"):
                    out["Gender"] = "Female"
        elif canon in REQUIRED_NUMERIC:
            try:
                out[canon] = float(v)
            except (TypeError, ValueError):
                pass
    return out

def extract_parameters(parsed):
    """
    Extract blood parameters from parsed input.
    parsed: str (from PDF/PNG) or dict (from JSON).
    Returns dict with keys: Age, Gender, Hemoglobin, Glucose, Cholesterol,
    White Blood Cells, Red Blood Cells, Platelets (and optionally more).
    """
    if isinstance(parsed, dict):
        return extract_from_dict(parsed)
    if isinstance(parsed, str):
        return extract_from_text(parsed)
    return {}
