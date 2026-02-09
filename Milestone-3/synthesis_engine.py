def synthesize_findings(model1_status, model2_patterns, risk_score, risk_level):
    findings = []
    systems = set()

    for name, _, _ in model2_patterns:

        if name == "Diabetic Risk":
            findings.append("Elevated blood glucose indicating diabetes risk")
            systems.add("Metabolic")

        elif name == "Cardiovascular Risk":
            findings.append("High cholesterol increasing cardiovascular risk")
            systems.add("Cardiovascular")

        elif name == "Anemia Risk":
            findings.append("Hemoglobin and RBC abnormalities suggesting anemia")
            systems.add("Hematologic")

        elif name == "Immunity Risk":
            findings.append("Abnormal WBC count indicating immunity or infection concern")
            systems.add("Immune")

        elif name == "Metabolic Syndrome Risk":
            findings.append("Combined glucose and cholesterol abnormalities indicating metabolic syndrome")
            systems.add("Metabolic")

        elif name == "Blood Clotting Risk":
            findings.append("Severely abnormal hemoglobin and RBC indicating clotting risk")
            systems.add("Hematologic")

        elif name == "Oxygen Transport Deficiency":
            findings.append("Hb and WBC abnormalities affecting oxygen transport")
            systems.add("Respiratory")

        elif name == "Chronic Inflammatory Stress":
            findings.append("WBC and cholesterol imbalance indicating chronic inflammation")
            systems.add("Immune")

        elif name == "Circulatory System Weakness":
            findings.append("RBC and cholesterol abnormalities affecting circulation")
            systems.add("Cardiovascular")

        elif name == "Metabolic Fatigue Syndrome":
            findings.append("Glucose and hemoglobin imbalance leading to metabolic fatigue")
            systems.add("Metabolic")

        elif name == "Bleeding Risk":
            findings.append("Low platelet count indicating bleeding risk")
            systems.add("Hematologic")

    # If no patterns detected
    if not findings:
        findings.append("All blood parameters are within normal range indicating stable health")
        systems.add("General")

    
    pattern_count = len(model2_patterns)

    if pattern_count >= 6 and risk_level != "High":
        risk_level = "High"

    elif pattern_count >= 3 and risk_level == "Low":
        risk_level = "Medium"
    

    return {
        "key_findings": findings,
        "overall_risk": risk_level,
        "risk_score": risk_score,
        "affected_systems": list(systems)
    }
