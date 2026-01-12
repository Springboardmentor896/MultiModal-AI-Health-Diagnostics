from src.data_ingestion import ingest_blood_report
from src.blood_report_parser import parse_report
from src.model_parameter_interpreter import interpret_parameters

import pandas as pd
import os

FOLDER_PATH = "data/raw"
OUTPUT_PATH = "data/processed"

os.makedirs(OUTPUT_PATH, exist_ok=True)

i = 1

for file in os.listdir(FOLDER_PATH):
    file_path = os.path.join(FOLDER_PATH, file)

    if not os.path.isfile(file_path):
        continue

    print(f"\nProcessing: {file}")

    text = ingest_blood_report(file_path)
    
    params, sex = parse_report(text)
    
    results = interpret_parameters(params, sex)

    print("Extracted values:", params)
    print("Interpretation:")
    for k, v in results.items():
        print(f"  {k} -> {v['status']}")

    df = pd.DataFrame([params])
    df.to_csv(
        os.path.join(OUTPUT_PATH, f"interpretations_{i}.csv"),
        index=False
    )

    i += 1
