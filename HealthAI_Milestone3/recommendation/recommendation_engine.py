
def generate_recommendations(summary):
    recommendations = []

    for finding in summary.get("key_findings", []):
        f = finding.lower()

        if "anemia" in f:
            recommendations.append(
                "Increase iron-rich foods and consult a physician if symptoms persist."
            )

        if "glucose" in f or "diabetes" in f:
            recommendations.append(
                "Reduce sugar intake, increase physical activity, and consider HbA1c testing."
            )

        if "cholesterol" in f:
            recommendations.append(
                "Adopt a low-fat diet, avoid fried foods, and include daily walking."
            )

    return recommendations
