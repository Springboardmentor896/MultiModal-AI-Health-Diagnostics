def generate_recommendations(summary, age, gender):
    recs = []
    handled = set()

    for finding in summary["key_findings"]:
        f = finding.lower()

        # Anemia related
        if "anemia" in f or "hemoglobin" in f:
            if "anemia" not in handled:
                recs.append(
                    "Increase iron-rich foods like spinach and dates; consider ferritin test if fatigue persists."
                )
                handled.add("anemia")

        # Immunity / infection related
        if "wbc" in f or "infection" in f or "oxygen transport" in f:
            if "immunity" not in handled:
                recs.append(
                    "Ensure adequate hydration, rest, and consult a doctor if fever or weakness continues."
                )
                handled.add("immunity")

        # Cholesterol / cardio
        if "cholesterol" in f or "cardio" in f:
            if "cardio" not in handled:
                recs.append(
                    "Adopt a low-fat diet, include brisk walking, and consult a physician for lipid control."
                )
                handled.add("cardio")

        # Glucose / diabetes
        if "glucose" in f or "diabetes" in f:
            if "diabetes" not in handled:
                recs.append(
                    "Reduce intake of sugary foods, perform daily exercise, and consider HbA1c testing."
                )
                handled.add("diabetes")

        # Platelets / bleeding
        if "platelet" in f or "bleeding" in f:
            if "bleeding" not in handled:
                recs.append(
                    "Avoid injury-prone activities and consult a doctor for platelet evaluation."
                )
                handled.add("bleeding")

    # Context advice
    if age > 55:
        recs.append("Schedule regular full body checkups every 6 months.")

    if gender.lower() == "male":
        recs.append("Maintain heart health with regular cardio exercise.")

    # Normal case
    if not recs:
        recs.append("Stay hydrated, Maintain a balanced diet and regular physical activity.")
        

    return recs
