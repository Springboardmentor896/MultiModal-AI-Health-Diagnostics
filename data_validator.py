import pandas as pd

def validate_row(row):
    required = [
        "Age",
        "Hemoglobin",
        "Glucose",
        "Cholesterol",
        "White Blood Cells",
        "Red Blood Cells"
    ]

    for col in required:
        if col not in row:
            return False

        value = row[col]

        if pd.isna(value):
            return False

        try:
            float(value)
        except:
            return False

    return True
