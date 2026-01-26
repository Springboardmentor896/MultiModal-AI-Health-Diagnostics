def detect_patterns(status_dict, age):
    patterns = []

    g = status_dict["Glucose"]
    c = status_dict["Cholesterol"]
    h = status_dict["Hemoglobin"]
    w = status_dict["White Blood Cells"]
    r = status_dict["Red Blood Cells"]

    # Cardiovascular risk
    if g == "High" and c == "High":
        score = 4.5 + (1 if age > 50 else 0)
        severity = "High" if score >= 5 else "Medium"
        patterns.append(("Cardiovascular risk", score, severity))

    # Metabolic risk
    if g == "High" and r == "Low":
        patterns.append(("Metabolic risk", 1.0, "Low"))

    # Infection / Inflammation risk
    if w == "High" and h == "High":
        patterns.append(("Infection/Inflammation risk", 2.5, "Medium"))

    # Anemia risk
    if h == "Low" and r == "Low":
        patterns.append(("Anemia risk", 3.0, "Medium"))

    # Diabetic risk
    if g == "High" and h == "Low":
        patterns.append(("Diabetic risk", 3.5, "High"))

    # Immune system risk
    if w == "Low" and h == "Low":
        patterns.append(("Immune system risk", 2.0, "Medium"))

    # Blood viscosity risk
    if h == "High" and r == "High":
        patterns.append(("Blood viscosity risk", 3.0, "Medium"))

    # Chronic disease stress
    if g == "High" and c == "High" and w == "High":
        patterns.append(("Chronic disease stress", 5.0, "High"))

    # Oxygen transport risk
    if h == "Low" and w == "High":
        patterns.append(("Oxygen transport risk", 2.5, "Medium"))

    return patterns
