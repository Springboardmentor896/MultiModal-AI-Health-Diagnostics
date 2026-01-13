from ingestion.pdf_parser import extract_text_from_pdf
from ingestion.csv_parser import read_csv_file
from ingestion.image_parser import extract_text_from_image

from extraction.parameter_extractor import extract_parameters
from validation.standardizer import classify_parameters
from models.model1_parameter_interpreter import interpret_parameters

file_path = "data/raw_reports/sample.pdf"

if file_path.endswith(".pdf"):
    text = extract_text_from_pdf(file_path)
    parameters = extract_parameters(text)

elif file_path.endswith(".jpg") or file_path.endswith(".png"):
    text = extract_text_from_image(file_path)
    parameters = extract_parameters(text)

elif file_path.endswith(".csv"):
    df = read_csv_file(file_path)
    parameters = {k.lower(): float(v) for k, v in df.iloc[0].to_dict().items()}


else:
    raise ValueError("Unsupported file format")

classification = classify_parameters(parameters)

interpretation = interpret_parameters(parameters, classification)

print("\nExtracted Values:")
for k, v in parameters.items():
    print(f"{k}: {v}")

print("\nStatus:")
for k, v in classification.items():
    print(f"{k}: {v}")

print("\nInterpretation:")
for k, v in interpretation.items():
    print(f"{k}: {v}")


