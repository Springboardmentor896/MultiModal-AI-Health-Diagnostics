def identify_patterns(data):
    patterns = []

    hb = data.get("Hemoglobin")
    platelets = data.get("Platelets")

    # 1. Anemia
    if hb is not None and hb < 13:
        patterns.append({
            "condition": "Anemia Pattern",
            "severity": "Low" if hb >= 11 else "Medium"
        })

    # 2. platelets
    if platelets is not None and platelets <= 150000:
        patterns.append({
            "condition": "Platelet Risk",
            "severity": "Low"
        })

    # 3. Cardiovascular Risk
    if hb is not None and platelets is not None:
        if hb < 13 and platelets > 300000:
            patterns.append({
                "condition": "Cardiovascular Risk Indicator",
                "severity": "Medium"
            })

    # 4. Metabolic Risk
    if hb is not None and platelets is not None:
        if hb >= 13 and platelets <= 150000:
            patterns.append({
                "condition": "Metabolic Imbalance Risk",
                "severity": "Low"
            })

    # 5. Diabetes Risk 
    if platelets is not None and hb is not None:
        if platelets <= 150000 and hb <= 13:
            patterns.append({
                "condition": "Diabetes Risk",
                "severity": "Low"
            })

    # 6. Overall Health Stress
    if len(patterns) >= 2:
        patterns.append({
            "condition": "General Health Stress Indicator",
            "severity": "Medium"
        })

    return patterns
