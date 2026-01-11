import pandas as pd

REQUIRED_COLUMNS = [
    "Glucose",
    "Cholesterol",
    "Hemoglobin",
    "White Blood Cells",
    "Red Blood Cells"
]

def validate_and_clean(df):
    df = df[REQUIRED_COLUMNS].copy()

    for col in REQUIRED_COLUMNS:
        df.loc[:, col] = df[col].apply(
            lambda x: x if 0 <= x <= 1 else None
        )

    return df.dropna()
