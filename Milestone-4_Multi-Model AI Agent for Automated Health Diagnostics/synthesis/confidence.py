"""
Confidence Estimator: estimate reliability of the analysis from data completeness/quality.
"""
def calculate_confidence(data) -> float:
    """
    Return confidence 0–100 based on presence, plausibility, and data quality.
    data: validated dict from ingestion (required keys present).
    """
    if not data:
        return 0.0

    required = [
        "Hemoglobin", "Glucose", "Cholesterol",
        "White Blood Cells", "Red Blood Cells", "Platelets",
        "Age", "Gender",
    ]

    # -------------------------
    # 1. COMPLETENESS (40%)
    # -------------------------
    present = sum(1 for k in required if data.get(k) is not None and data.get(k) != "")
    completeness_score = present / len(required)  # 0–1

    # -------------------------
    # 2. PLAUSIBILITY CHECK (30%)
    # Penalize extreme values
    # -------------------------
    plausible = 0
    for k in required:
        v = data.get(k)
        if v is None:
            continue

        try:
            v = float(v) if k not in ("Gender",) else v

            if k == "Hemoglobin" and 2 <= v <= 25:
                plausible += 1
            elif k == "Glucose" and 40 <= v <= 500:
                plausible += 1
            elif k == "Cholesterol" and 50 <= v <= 400:
                plausible += 1
            elif k == "White Blood Cells" and 1000 <= v <= 50000:
                plausible += 1
            elif k == "Red Blood Cells" and 1 <= v <= 10:
                plausible += 1
            elif k == "Platelets" and 10000 <= v <= 1000000:
                plausible += 1
            elif k == "Age" and 1 <= v <= 120:
                plausible += 1
            elif k == "Gender" and str(v).lower() in ("male", "female"):
                plausible += 1

        except Exception:
            continue

    plausibility_score = plausible / len(required)  # 0–1

    # -------------------------
    # 3. CONSISTENCY CHECK (30%)
    # Penalize unrealistic combinations
    # -------------------------
    consistency_penalty = 0

    try:
        hb = float(data.get("Hemoglobin", 0))
        rbc = float(data.get("Red Blood Cells", 0))
        wbc = float(data.get("White Blood Cells", 0))

        # Example inconsistencies
        if hb < 5 and rbc > 6:
            consistency_penalty += 1  # conflicting anemia signals

        if wbc > 20000 and hb > 18:
            consistency_penalty += 1  # unlikely combo

    except Exception:
        pass

    # Normalize penalty
    consistency_score = max(0, 1 - (consistency_penalty / 2))

    # -------------------------
    # FINAL WEIGHTED SCORE
    # -------------------------
    confidence = (
        completeness_score * 40 +
        plausibility_score * 30 +
        consistency_score * 30
    )

    return round(max(0.0, min(100.0, confidence)), 1)