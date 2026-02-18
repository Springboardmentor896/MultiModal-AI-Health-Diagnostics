def contextual_adjustment(data, age=None, gender=None, is_pregnant=False):
    context_flags = []
    try:
        age = int(age) if age else 35
    except ValueError:
        age = 35

    if age > 60:
        if "hemoglobin" in data:
            data["hemoglobin"] -= 0.5
        if "wbc" in data:
            data["wbc"] -= 300
        if "glucose" in data:
            data["glucose"] += 5
        if "creatinine" in data:
            data["creatinine"] += 0.1
        context_flags.append("Senior baseline adjustments applied.")

    elif age < 12:
        if "hemoglobin" in data:
            data["hemoglobin"] += 0.5
        if "rbc" in data:
            data["rbc"] += 0.3
        context_flags.append("Pediatric growth baseline adjustments applied.")

    if gender and gender.lower() == "female" and is_pregnant:
        if "hemoglobin" in data:
            data["hemoglobin"] -= 1.0
        if "platelets" in data:
            data["platelets"] -= 30000
        context_flags.append("Pregnancy-specific physiological markers applied.")

    return context_flags