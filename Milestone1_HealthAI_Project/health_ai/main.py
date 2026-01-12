import os
from extraction.ocr_engine import extract_text
from extraction.parameter_extractor import extract_parameters
from validation.standardizer import standardize
from models.model1_parameter_interpreter import interpret

IMAGE_FOLDER = "data/images"

print("\n===== Milestone-1: Batch Blood Report Analysis =====\n")

for file in os.listdir(IMAGE_FOLDER):
    if file.endswith(".png") or file.endswith(".jpg"):
        image_path = os.path.join(IMAGE_FOLDER, file)

        print(f"Processing: {file}")

        text = extract_text(image_path)
        params = extract_parameters(text)
        clean = standardize(params)
        result = interpret(clean)

        for k, v in result.items():
            print(f"  {k}: {v['value']} -> {v['status']}")

        print("-" * 50)
