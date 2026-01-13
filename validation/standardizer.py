REFERENCE_RANGES = {
    "hemoglobin": (12, 17),
    "wbc": (4000, 11000),
    "rbc": (4.0, 6.0),
    "platelets": (150000, 450000),
    "glucose": (70, 110)
}

def classify_parameters(values):
    status = {}

    for parameters, value in values.items():
        key = parameters.lower().strip()   # normalize extracted param

        if key not in REFERENCE_RANGES:
            status[parameters] = "Unknown"
            continue

        low, high = REFERENCE_RANGES[key]

        if value < low:
            status[parameters] = "Low"
        elif value > high:
            status[parameters] = "High"
        else:
            status[parameters] = "Normal"

    return status
