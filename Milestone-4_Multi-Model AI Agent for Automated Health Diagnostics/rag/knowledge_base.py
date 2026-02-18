"""
Knowledge base for medical guidelines (RAG / retrieval).
"""
MEDICAL_GUIDELINES = {
    "High LDL": "Reduce saturated fat, increase fiber intake.",
    "High Glucose": "Limit sugar intake and increase physical activity.",
    "High Cholesterol": "Adopt a low-fat diet and consider statins under physician guidance.",
    "Low Hemoglobin": "Increase iron-rich foods; consider ferritin test if fatigue persists.",
    "Anemia": "Increase iron-rich foods like spinach and dates; consider ferritin test if fatigue persists.",
}

def retrieve_guideline(condition: str) -> str:
    """Return guideline text for a condition, or empty string if not found."""
    key = (condition or "").strip()
    if not key:
        return ""
    return MEDICAL_GUIDELINES.get(key, "")
