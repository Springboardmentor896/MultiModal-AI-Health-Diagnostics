import os
from extraction.ocr_engine import extract_text
from extraction.parameter_extractor import extract_parameters
from validation.standardizer import standardize
from models.model1_parameter_interpreter import interpret as model1_interpret
from model2_pattern_engine import interpret as model2_interpret

IMAGE_FOLDER = "data/images"

print("\n===== Milestone-1: Batch Blood Report Analysis =====\n")

for file in os.listdir(IMAGE_FOLDER):
    if file.endswith(".png") or file.endswith(".jpg"):
        image_path = os.path.join(IMAGE_FOLDER, file)

        print(f"Processing: {file}")

        text = extract_text(image_path)
        params = extract_parameters(text)
        clean = standardize(params)
        
        # Model 1: Parameter Interpretation
        result = model1_interpret(clean)

        print("\n--- MODEL 1: Parameter Status ---")
        for k, v in result.items():
            print(f"  {k}: {v['value']} -> {v['status']}")
        
        # Model 2: Pattern Recognition & Risk Assessment
        print("\n--- MODEL 2: Pattern Recognition & Risk Assessment ---")
        risk_report = model2_interpret(clean)
        
        # Display lipid ratios if available
        if risk_report["lipid_ratios"]:
            print("\nLipid Ratios:")
            for ratio_name, ratio_data in risk_report["lipid_ratios"].items():
                print(f"  {ratio_name.replace('_', '/').upper()}: {ratio_data['value']} [{ratio_data['risk_level']} Risk]")
        
        # Display identified patterns
        if risk_report["identified_patterns"]:
            print("\nIdentified Patterns:")
            for pattern in risk_report["identified_patterns"]:
                print(f"  - {pattern['pattern']} [{pattern['severity']}]")
        
        # Display risk assessments
        print("\nRisk Scores:")
        for risk_type, risk_data in risk_report["risk_assessments"].items():
            print(f"  {risk_type.replace('_', ' ').title()}: {risk_data['risk_level']} (Score: {risk_data['score']})")
        
        # Display overall assessment
        print(f"\nTotal Risk Score: {risk_report['overall_assessment']['total_risk_score']}")
        if risk_report['overall_assessment']['primary_concerns']:
            print("Primary Concerns:")
            for concern in risk_report['overall_assessment']['primary_concerns']:
                print(f"  - {concern}")

        print("-" * 80)
