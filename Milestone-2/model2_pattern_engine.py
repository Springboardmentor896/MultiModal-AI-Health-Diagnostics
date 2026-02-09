# ---------- POINT SCORING PER PARAMETER ----------

def get_points_glucose(g):
    if 70 <= g <= 140:
        return 0
    elif 141 <= g <= 200 or 60 <= g < 70:
        return 1
    else:
        return 2


def get_points_hb(h):
    if 12 <= h <= 17:
        return 0
    elif 10 <= h < 12 or 17 < h <= 19:
        return 1
    else:
        return 2


def get_points_cholesterol(c):
    if 150 <= c <= 240:
        return 0
    elif 241 <= c <= 280:
        return 1
    else:
        return 2


def get_points_rbc(r):
    if 4.2 <= r <= 6.1:
        return 0
    elif 3.8 <= r < 4.2 or 6.1 < r <= 6.5:
        return 1
    else:
        return 2


def get_points_wbc(w):
    if 4000 <= w <= 11000:
        return 0
    elif 3500 <= w < 4000 or 11000 < w <= 15000:
        return 1
    else:
        return 2


def get_points_platelets(p):
    if 150000 <= p <= 450000:
        return 0
    elif 120000 <= p < 150000 or 450000 < p <= 500000:
        return 1
    else:
        return 2


# ---------- TOTAL RISK SCORE ----------

def calculate_total_risk(row):
    g = float(row["Glucose"])
    h = float(row["Hemoglobin"])
    c = float(row["Cholesterol"])
    r = float(row["Red Blood Cells"])
    w = float(row["White Blood Cells"])
    p = float(row["Platelets"])

    total_score = (
        get_points_glucose(g)
        + get_points_hb(h)
        + get_points_cholesterol(c)
        + get_points_rbc(r)
        + get_points_wbc(w)
        + get_points_platelets(p)
    )

    return total_score


# ---------- SEVERITY ----------

def get_severity(score):
    if score <= 4:
        return "Low"
    elif score <= 9:
        return "Medium"
    else:
        return "High"


# ---------- PATTERN DETECTION (MODEL-2) ----------

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
    age = int(row["Age"])

    # Diabetic Risk
    if get_points_glucose(g) >= 1:
        patterns.append(("Diabetic Risk", round(score * 0.4, 1), severity))

    # Cardiovascular Risk
    if get_points_cholesterol(c) >= 1:
        patterns.append(("Cardiovascular Risk", round(score * 0.4, 1), severity))

    # Anemia Risk
    if get_points_hb(h) >= 1 and get_points_rbc(r) >= 1:
        patterns.append(("Anemia Risk", round(score * 0.3, 1), severity))

    # Immunity Risk
    if get_points_wbc(w) >= 1:
        patterns.append(("Immunity Risk", round(score * 0.3, 1), severity))

    # Metabolic Syndrome Risk
    if get_points_glucose(g) >= 1 and get_points_cholesterol(c) >= 1:
        patterns.append(("Metabolic Syndrome Risk", round(score * 0.5, 1), severity))

    # Blood Clotting Risk
    if get_points_hb(h) == 2 and get_points_rbc(r) == 2:
        patterns.append(("Blood Clotting Risk", round(score * 0.4, 1), severity))

    # Oxygen Transport Deficiency
    if get_points_hb(h) >= 1 and get_points_wbc(w) >= 1:
        patterns.append(("Oxygen Transport Deficiency", round(score * 0.3, 1), severity))

    # Chronic Inflammatory Stress
    if get_points_wbc(w) >= 1 and get_points_cholesterol(c) >= 1:
        patterns.append(("Chronic Inflammatory Stress", round(score * 0.4, 1), severity))

    # Circulatory System Weakness
    if get_points_rbc(r) >= 1 and get_points_cholesterol(c) >= 1:
        patterns.append(("Circulatory System Weakness", round(score * 0.4, 1), severity))

    # Metabolic Fatigue Syndrome (purely blood based)
    if get_points_glucose(g) >= 1 and get_points_hb(h) >= 1:
        patterns.append(("Metabolic Fatigue Syndrome", round(score * 0.5, 1), severity))


    # Bleeding Risk (Platelets)
    if get_points_platelets(p) >= 1:
        patterns.append(("Bleeding Risk", round(score * 0.4, 1), severity))

    return patterns
