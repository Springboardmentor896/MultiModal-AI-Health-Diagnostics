
def synthesize_findings(data):
    findings = []

    # Anemia
    if data.get("hemoglobin", 15) < 13:
        findings.append("Low hemoglobin indicating anemia")

    # Diabetes risk
    if data.get("glucose", 90) > 100:
        findings.append("Elevated glucose indicating diabetes risk")

    # Cardiovascular risk
    if data.get("cholesterol", 180) > 200:
        findings.append("High cholesterol increasing cardiovascular risk")

    risk = "Low" if len(findings) <= 1 else "Moderate" if len(findings) == 2 else "High"

    return {
        "key_findings": findings,
        "risk_level": risk
    }
