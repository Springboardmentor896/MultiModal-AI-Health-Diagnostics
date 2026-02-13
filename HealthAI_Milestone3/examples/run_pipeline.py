import sys
import os
import json
from datetime import datetime

# -------------------------------------------------
# Add project root to Python path
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from synthesis.synthesis_engine import synthesize_findings
from recommendation.recommendation_engine import generate_recommendations


# -------------------------------------------------
# Automatically load ALL OCR mock files (ALL patients)
# -------------------------------------------------
OCR_DIR = os.path.join(PROJECT_ROOT, "ocr_mock_outputs")
ocr_files = sorted([f for f in os.listdir(OCR_DIR) if f.endswith(".json")])


# -------------------------------------------------
# Main execution loop
# -------------------------------------------------
for idx, file_name in enumerate(ocr_files, start=1):

    with open(os.path.join(OCR_DIR, file_name)) as f:
        extracted_data = json.load(f)

    patient_id = f"PAT-{1000 + idx}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary = synthesize_findings(extracted_data)
    recommendations = generate_recommendations(summary)

    print("=" * 70)
    print(f"PATIENT {idx} | Patient ID: {patient_id}")
    print(f"Generated On: {timestamp}")
    print("=" * 70)

    print("\nSYNTHESIZED SUMMARY")
    if summary["key_findings"]:
        for finding in summary["key_findings"]:
            print(f"- {finding}")
    else:
        print("- No significant abnormalities detected")

    print(f"\nOverall Risk: {summary['risk_level']}")

    print("\nRECOMMENDATIONS")
    if recommendations:
        for rec in recommendations:
            print(f"- {rec}")
    else:
        print("- Maintain a healthy lifestyle and routine checkups")

    print("\n")

