"""
Findings Synthesis Engine
"""

def synthesize(m1, risk, context_flags):

    abnormal = [p for p, status in m1.items() if status != "Normal"]

    level = context_flags.get("risk_level") or risk.get("level", "Low")
    score = context_flags.get("adjusted_score") or risk.get("score", 0)

    risk_probability = min(100, max(0, round(score * 10)))
    context_notes = list(context_flags.get("context_notes") or [])

    key_findings = []
    patterns = risk.get("patterns") or []

    def pattern_relevant(name: str) -> bool:
        if name == "Diabetic Risk":
            return "Glucose" in abnormal

        if name == "Cardiovascular Risk":
            return "Cholesterol" in abnormal

        if name == "Anemia Risk":
            return ("Hemoglobin" in abnormal) or ("Red Blood Cells" in abnormal)

        if name == "Immunity Risk":
            return "White Blood Cells" in abnormal

        if name == "Metabolic Syndrome Risk":
            return ("Glucose" in abnormal) or ("Cholesterol" in abnormal)

        if name == "Blood Clotting Risk":
            return ("Hemoglobin" in abnormal) or ("Red Blood Cells" in abnormal)

        if name == "Oxygen Transport Deficiency":
            return ("Hemoglobin" in abnormal) or ("White Blood Cells" in abnormal)

        if name == "Chronic Inflammatory Stress":
            return ("White Blood Cells" in abnormal) or ("Cholesterol" in abnormal)

        if name == "Circulatory System Weakness":
            return ("Red Blood Cells" in abnormal) or ("Cholesterol" in abnormal)

        if name == "Metabolic Fatigue Syndrome":
            return ("Glucose" in abnormal) or ("Hemoglobin" in abnormal)

        if name == "Bleeding Risk":
            return "Platelets" in abnormal

        return bool(abnormal)

    for name, _, _ in patterns:
        if not pattern_relevant(name):
            continue

        if name == "Diabetic Risk":
            key_findings.append("Elevated blood glucose indicating diabetes risk")

        elif name == "Cardiovascular Risk":
            key_findings.append("High cholesterol increasing cardiovascular risk")

        elif name == "Anemia Risk":
            key_findings.append("Hemoglobin or RBC abnormalities suggesting anemia")

        elif name == "Immunity Risk":
            key_findings.append("Abnormal WBC count indicating immunity concern")

        elif name == "Metabolic Syndrome Risk":
            key_findings.append("Combined metabolic irregularities observed")

        elif name == "Blood Clotting Risk":
            key_findings.append("Severe blood parameter imbalance affecting clotting")

        elif name == "Oxygen Transport Deficiency":
            key_findings.append("Blood parameters may affect oxygen transport")

        elif name == "Chronic Inflammatory Stress":
            key_findings.append("Indicators suggest possible inflammatory stress")

        elif name == "Circulatory System Weakness":
            key_findings.append("Circulatory system may be affected")

        elif name == "Metabolic Fatigue Syndrome":
            key_findings.append("Metabolic imbalance observed")

        elif name == "Bleeding Risk":
            key_findings.append("Platelet imbalance indicating bleeding risk")

        else:
            key_findings.append(name)

    # FINAL FALLBACK (improved)
    if not key_findings:
        if abnormal:
            for p in abnormal[:3]:
                key_findings.append(f"{p} is outside normal range")

        else:
            key_findings.append("All parameters are within normal limits")

    return {
        "abnormal_parameters": abnormal,
        "risk_level": level,
        "risk_probability": risk_probability,
        "context_notes": context_notes,
        "key_findings": key_findings[:6],
        "risk_score": score,
    }