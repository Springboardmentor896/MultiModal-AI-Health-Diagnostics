"""
Pattern Recognition & Risk Assessment Model (Model 2).
"""
# ---------- Point scoring per parameter ----------

def get_points_glucose(g):
    if 70 <= g <= 140:
        return 0
    elif 141 <= g <= 200 or 60 <= g < 70:
        return 1
    return 2

def get_points_hb(h):
    if 12 <= h <= 17:
        return 0
    elif 10 <= h < 12 or 17 < h <= 19:
        return 1
    return 2

def get_points_cholesterol(c):
    if 150 <= c <= 240:
        return 0
    elif 241 <= c <= 280:
        return 1
    return 2

def get_points_rbc(r):
    if 4.2 <= r <= 6.1:
        return 0
    elif 3.8 <= r < 4.2 or 6.1 < r <= 6.5:
        return 1
    return 2

def get_points_wbc(w):
    if 4000 <= w <= 11000:
        return 0
    elif 3500 <= w < 4000 or 11000 < w <= 15000:
        return 1
    return 2

def get_points_platelets(p):
    if 150000 <= p <= 450000:
        return 0
    elif 120000 <= p < 150000 or 450000 < p <= 500000:
        return 1
    return 2

# ---------- Total risk score ----------

def calculate_total_risk(row):
    g = float(row["Glucose"])
    h = float(row["Hemoglobin"])
    c = float(row["Cholesterol"])
    r = float(row["Red Blood Cells"])
    w = float(row["White Blood Cells"])
    p = float(row["Platelets"])
    return (
        get_points_glucose(g) + get_points_hb(h) + get_points_cholesterol(c)
        + get_points_rbc(r) + get_points_wbc(w) + get_points_platelets(p)
    )

def get_severity(score):
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    return "High"

# ---------- Pattern detection ----------

def detect_patterns(row):
    score = calculate_total_risk(row)
    severity = get_severity(score)
    patterns = []
    g = float(row["Glucose"])
    h = float(row["Hemoglobin"])
    c = float(row["Cholesterol"])
    r = float(row["Red Blood Cells"])
    w = float(row["White Blood Cells"])
    p = float(row["Platelets"])

    if get_points_glucose(g) >= 1:
        patterns.append(("Diabetic Risk", round(score * 0.4, 1), severity))
    if get_points_cholesterol(c) >= 1:
        patterns.append(("Cardiovascular Risk", round(score * 0.4, 1), severity))
    if get_points_hb(h) >= 1 and get_points_rbc(r) >= 1:
        patterns.append(("Anemia Risk", round(score * 0.3, 1), severity))
    if get_points_wbc(w) >= 1:
        patterns.append(("Immunity Risk", round(score * 0.3, 1), severity))
    if get_points_glucose(g) >= 1 and get_points_cholesterol(c) >= 1:
        patterns.append(("Metabolic Syndrome Risk", round(score * 0.5, 1), severity))
    if get_points_hb(h) == 2 and get_points_rbc(r) == 2:
        patterns.append(("Blood Clotting Risk", round(score * 0.4, 1), severity))
    if get_points_hb(h) >= 1 and get_points_wbc(w) >= 1:
        patterns.append(("Oxygen Transport Deficiency", round(score * 0.3, 1), severity))
    if get_points_wbc(w) >= 1 and get_points_cholesterol(c) >= 1:
        patterns.append(("Chronic Inflammatory Stress", round(score * 0.4, 1), severity))
    if get_points_rbc(r) >= 1 and get_points_cholesterol(c) >= 1:
        patterns.append(("Circulatory System Weakness", round(score * 0.4, 1), severity))
    if get_points_glucose(g) >= 1 and get_points_hb(h) >= 1:
        patterns.append(("Metabolic Fatigue Syndrome", round(score * 0.5, 1), severity))
    if get_points_platelets(p) >= 1:
        patterns.append(("Bleeding Risk", round(score * 0.4, 1), severity))
    return patterns

# ---------- Orchestrator API ----------

def calculate_risk(data, age=None):
    """
    Compute total risk score, severity, and patterns from validated data.
    Returns dict: score, level, patterns.
    """
    row = dict(data)
    if "Age" not in row:
        row["Age"] = age if age is not None else 35
    if "Gender" not in row:
        row["Gender"] = "Male"
    score = calculate_total_risk(row)
    level = get_severity(score)
    patterns = detect_patterns(row)
    return {"score": score, "level": level, "patterns": patterns}
