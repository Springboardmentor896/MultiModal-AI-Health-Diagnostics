from ingestion.extractor import extract_lab_data
from models.model1_interpreter import Model1Interpreter
from models.model2_ml_risk import Model2MLRisk
from models.model3_contextual import Model3Contextual

def run_test(label, text, patient):
    lab = extract_lab_data(text)
    m1 = Model1Interpreter()
    m2 = Model2MLRisk()
    m3 = Model3Contextual()

    r1 = m1.analyze(lab, patient)
    r2 = m2.analyze(lab, patient)
    r3 = m3.analyze(lab, patient, r1, r2)

    print(f"\n{'='*50}")
    print(f"TEST: {label}")
    print(f"{'='*50}")
    print(f"Extracted Lab Data: {lab}")
    print(f"\n--- Model 1 (Clinical Rules) ---")
    for d, r in r1['risks'].items():
        print(f"  {d}: {r['probability']*100:.1f}% ({r['label']})")
    print(f"\n--- Model 2 (ML Risk) ---")
    for d, r in r2['risks'].items():
        print(f"  {d}: {r['probability']*100:.1f}% ({r['label']}) - Conf: {r.get('confidence',0)}%")
    print(f"\n--- Model 3 Final ---")
    for d, r in r3['risks'].items():
        print(f"  {d}: {r['probability']*100:.1f}% ({r['label']})")
    print(f"\n  >> Overall Risk: {r3.get('overall_risk', 'N/A')}")


# TEST 1: Normal healthy male
run_test(
    "NORMAL - Healthy 25yo Male",
    """
    Hemoglobin (Hb) 15.0
    Total RBC count 5.0
    Total WBC count 7000
    Platelet Count 250000
    Neutrophils 55
    Lymphocytes 30
    """,
    {'age': 25, 'gender': 'male', 'pregnant': False}
)

# TEST 2: Severely anemic + high WBC (infection)
run_test(
    "ABNORMAL - Anemia + Infection",
    """
    Hemoglobin (Hb) 7.5
    Total RBC count 3.2
    Total WBC count 15000
    Platelet Count 90000
    Neutrophils 80
    Lymphocytes 15
    """,
    {'age': 45, 'gender': 'female', 'pregnant': False}
)

# TEST 3: Borderline case (your original values)
run_test(
    "BORDERLINE - Mild Anemia 21yo Male",
    """
    Hemoglobin (Hb) 12.5
    Total RBC count 5.2
    Total WBC count 9000
    Platelet Count 150000
    Neutrophils 60
    Lymphocytes 31
    """,
    {'age': 21, 'gender': 'male', 'pregnant': False}
)
