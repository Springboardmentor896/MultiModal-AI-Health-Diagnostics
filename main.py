from ingestion.pdf_parser import extract_text_from_pdf
from ingestion.csv_parser import read_csv_file
from ingestion.image_parser import extract_text_from_image

from extraction.parameter_extractor import extract_parameters
from validation.standardizer import classify_parameters
from models.model1 import interpret_parameters
from models.model2 import identify_patterns, calculate_risk_score
from models.model3 import contextual_interpretation

from synthesis.findings_engine import synthesize_findings
from synthesis.recommendation_engine import get_recommendations
from reporting.report_generator import generate_report

file_path="data/raw_reports/9.png"

if file_path.endswith(".pdf"):
    text=extract_text_from_pdf(file_path)
    parameters=extract_parameters(text)

elif file_path.endswith(".jpg") or file_path.endswith(".png"):
    text = extract_text_from_image(file_path)
    parameters = extract_parameters(text)

elif file_path.endswith(".csv"):
    df = read_csv_file(file_path)
    parameters = df.iloc[0].to_dict()

else:
    raise ValueError("Unsupported file format")

parameters = {k.strip().lower(): v for k, v in parameters.items()}
DEMOGRAPHIC_KEYS = {"patient_name", "gender", "age", "pregnant"}

demographics = {k: v for k, v in parameters.items() if k in DEMOGRAPHIC_KEYS}

clinical_params = {k: v for k, v in parameters.items() if k not in DEMOGRAPHIC_KEYS}

for key in DEMOGRAPHIC_KEYS:
    clinical_params.pop(key, None)

adjusted_clinical = contextual_interpretation(clinical_params, demographics)

classification = classify_parameters(adjusted_clinical)

model2_input = {**adjusted_clinical, **demographics}
risk_patterns = identify_patterns(model2_input)
risk_score = calculate_risk_score(model2_input)

risk_data = {
    "risk_score": risk_score,
    "risk_patterns": risk_patterns,
    "risk_level": "High" if risk_score >= 6 else "Moderate" if risk_score >= 3 else "Low"
}

summary = synthesize_findings(classification, risk_data)

basic_advice = get_recommendations(summary)

generate_report(summary, basic_advice)