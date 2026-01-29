# Numerical risk score mapping
RISK_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}

def apply_context(patterns, age=None, gender=None):
    updated = []

    for p in patterns:
        severity = p["severity"]

        # Context-based severity adjustment
        if age is not None and age > 40:
            severity = "Medium"

        result = {
            "age": age,
            "gender": gender,
            "condition": p["condition"],
            "severity": severity,
            "severity_score": RISK_MAP[severity]
        }

        # Gender-specific notes
        if gender == "Female" and p["condition"] == "Anemia Pattern":
            result["note"] = "Female hemoglobin threshold considered"
        elif gender == "Male" and p["condition"] == "Cardiovascular Risk Indicator":
            result["note"] = "Male cardiovascular risk baseline applied"

        updated.append(result)

    return updated
