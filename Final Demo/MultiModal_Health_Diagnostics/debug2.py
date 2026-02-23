from ingestion.extractor import extract_lab_data
from models.model1_interpreter import Model1Interpreter
from models.model2_ml_risk import Model2MLRisk
from models.model3_contextual import Model3Contextual

test_text = """
Hemoglobin (Hb) 12.5
Total RBC count 5.2
Total WBC count 9000
Platelet Count 150000
Neutrophils 60
Lymphocytes 31
"""

lab = extract_lab_data(test_text)
patient = {'age': 21, 'gender': 'male', 'pregnant': False}

m1 = Model1Interpreter()
m2 = Model2MLRisk()
m3 = Model3Contextual()

r1 = m1.analyze(lab, patient)
r2 = m2.analyze(lab, patient)
r3 = m3.analyze(lab, patient, r1, r2)

print('=== MODEL 1 (Should be mostly LOW) ===')
for d, r in r1['risks'].items():
    print(f'{d}: {r["probability"]*100:.1f}% ({r["label"]})')

print('\n=== MODEL 2 (Should be mostly LOW) ===')
for d, r in r2['risks'].items():
    print(f'{d}: {r["probability"]*100:.1f}% ({r["label"]}) - Conf: {r.get("confidence",0)}%')

print('\n=== MODEL 3 FINAL (Should be mostly LOW) ===')
for d, r in r3['risks'].items():
    print(f'{d}: {r["probability"]*100:.1f}% ({r["label"]})')
