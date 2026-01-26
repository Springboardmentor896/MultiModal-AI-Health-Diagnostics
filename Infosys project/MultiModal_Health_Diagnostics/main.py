# ================================
# main.py
# MultiModal Health Diagnostics
# ================================

import os

# --------- INPUT ROUTER ----------
from ingestion_03.input_router import parse_input

# --------- PARAMETER EXTRACTION ----------
from processing_04.parameter_extraction import extract_parameters

# --------- INTERPRETATION (WITH CONTEXT) ----------
from processing_04.interpretation import interpret_with_context

# --------- DEVIATION CALCULATION ----------
from processing_04.deviation_calculator import calculate_deviation

# --------- DISEASE RISK ENGINE ----------
from processing_04.disease_engine import assess_disease_risks


# ================================
# PATH SETUP (IMPORTANT)
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(
    BASE_DIR,
    "input_01",
    "sample_report.pdf"   # change filename if needed
)


# ================================
# CONTEXT (Milestone 2 – Contextual Embeddings)
# ================================
context = {
    "gender": "female",        # male / female
    "age": 28,                 # years
    "pregnant": False          # True / False
}


# ================================
# PIPELINE START
# ================================

# 1️⃣ Read input (PDF / Image / CSV)
raw_text = parse_input(file_path)

# 2️⃣ Extract numeric parameters
extracted_parameters = extract_parameters(raw_text)

# 3️⃣ Interpret parameters with medical + contextual ranges
parameter_status = interpret_with_context(
    extracted_parameters,
    context=context
)

# 4️⃣ Calculate deviation from normal range (in %)
deviations = calculate_deviation(
    extracted_parameters,
    context=context
)


# ================================
# OUTPUT — MILESTONE 1
# ================================
print("\n📊 Context-Aware Parameter Status:")
for param, status in parameter_status.items():
    print(f"{param.upper()} → {status}")


# ================================
# MILESTONE 2 — DISEASE RISK
# ================================
disease_risks = assess_disease_risks(
    parameters=extracted_parameters,
    parameter_status=parameter_status,
    deviations=deviations
)


print("\n🧠 Disease Risk Assessment")

for disease, info in disease_risks.items():
    print(f"\n🩺 {disease}")
    print(f"Risk Probability: {info['risk_probability']}%")
    print(f"Risk Level: {info['risk_level']}")
    print("Why:")
    for reason in info["explanation"]:
        print(f" - {reason}")
