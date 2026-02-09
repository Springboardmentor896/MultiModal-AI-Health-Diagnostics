RANGES = {
    "Hemoglobin": (12, 16),
    "Glucose": (70, 110),
    "Cholesterol": (125, 200),
    "White Blood Cells": (4000, 11000),
    "Red Blood Cells": (4.2, 5.9),
    "Platelets": (150000, 450000)
}

def classify_parameter(value, param):
    low, high = RANGES[param]
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"

def interpret_blood_report(row):
    return {p: classify_parameter(float(row[p]), p) for p in RANGES}
