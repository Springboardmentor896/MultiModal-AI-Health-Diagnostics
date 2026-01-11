import pandas as pd


def load_blood_dataset(path):
    return pd.read_csv(path)

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

def classify_parameter(value):
    if value < 0.33:
        return "Low"
    elif value < 0.66:
        return "Normal"
    else:
        return "High"

def interpret_row(row):
    return {k: classify_parameter(v) for k, v in row.items()}

df = load_blood_dataset("blood_dataset.csv")
clean_df = validate_and_clean(df)

interpreted_series = clean_df.apply(interpret_row, axis=1)

for idx, patient_data in enumerate(interpreted_series):
    print(f"Patient {idx + 1}")
    for key, value in patient_data.items():
        print(f"{key}: {value}")
    print()
