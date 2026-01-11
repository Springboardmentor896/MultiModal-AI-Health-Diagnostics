import pandas as pd

DATASET_PATH = "blood_dataset.csv"

def load_blood_dataset(path):
    return pd.read_csv(path)

df = load_blood_dataset(DATASET_PATH)
df.head()
