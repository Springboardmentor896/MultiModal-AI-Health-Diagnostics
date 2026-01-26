import pandas as pd

def load_dataset(path="blood_dataset.csv"):
    df = pd.read_csv(path)

    required_cols = [
        "Age",
        "Hemoglobin",
        "Glucose",
        "Cholesterol",
        "White Blood Cells",
        "Red Blood Cells"
    ]

    return df[required_cols]
