def classify_parameter(value):
    if value < 0.33:
        return "Low"
    elif value > 0.66:
        return "High"
    else:
        return "Normal"


def interpret_blood_report(row):
    parameters = [
        "Hemoglobin",
        "Glucose",
        "Cholesterol",
        "White Blood Cells",
        "Red Blood Cells"
    ]

    status_dict = {}

    for param in parameters:
        value = float(row[param])
        status_dict[param] = classify_parameter(value)

    return status_dict
