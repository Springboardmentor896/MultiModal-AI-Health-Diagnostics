import os
from ocr.ocr_engine import extract_parameters
from integration.orchestrator import run

IMAGE_DIR = "input_data/images"

AGE = 39
GENDER = "Male"

for img in os.listdir(IMAGE_DIR):
    print("\nProcessing:", img)

    img_path = os.path.join(IMAGE_DIR, img)
    extracted = extract_parameters(img_path)
    print("Extracted:", extracted)

    results = run(extracted, age=AGE, gender=GENDER)

    print(f"\nAge: {AGE}")
    print(f"Gender: {GENDER}")

    print("\nDetected Risks:")
    for r in results:
        print(
            f"- {r['condition']} "
            f"(Severity: {r['severity']}, Risk Score: {r['severity_score']})"
        )
