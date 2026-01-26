import import_ipynb
from data_ingestion import load_dataset
from data_validator import validate_row
from model_parameter_interpreter import interpret_blood_report
from pattern_recognition_model import detect_patterns

df = load_dataset()

for i, row in df.iterrows():
    if not validate_row(row):
        continue

    status = interpret_blood_report(row)
    age = int(row["Age"])
    patterns = detect_patterns(status, age)

    print(f"\nPatient {i+1}")
    print(f"Age - {age}\n")

    for param in status:
        print(f"{param}: {row[param]:.6f} → {status[param]}")

    print("\n\nPatterns Detected:")
    if patterns:
        for name, score, severity in patterns:
            print(f"{name} (Risk Score - {score}, Severity - {severity})")
    else:
        print("None")

    print("-" * 60)
