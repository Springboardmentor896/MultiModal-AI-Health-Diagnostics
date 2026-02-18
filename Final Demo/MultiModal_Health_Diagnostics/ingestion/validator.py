from typing import Dict, Any, List

# Critical parameters that should be present
REQUIRED_PARAMS = ["Hemoglobin", "Fasting_Glucose", "Total_Cholesterol"]

def validate_extracted(extracted: Dict[str, float]) -> Dict[str, Any]:
    """
    Validate extracted parameters: check numeric, non-negative, required present.
    
    Args:
        extracted: {param: value} from extractor
    
    Returns:
        {
            "validated": {param: value} - cleaned data,
            "issues": [str] - problems found,
            "confidence": str - low/medium/high,
            "missing": [str] - critical params missing
        }
    """
    issues = []
    validated = {}
    
    # Check each parameter
    for param, value in extracted.items():
        # Must be numeric
        if not isinstance(value, (int, float)):
            issues.append(f"{param}: non-numeric value {value}")
            continue
        
        # Must be non-negative
        if value < 0:
            issues.append(f"{param}: negative value {value}")
            continue
        
        # Sanity range checks (very loose - just catch obvious errors)
        if param == "Hemoglobin" and (value < 1 or value > 25):
            issues.append(f"{param}: value {value} out of plausible range (1-25)")
        elif param == "Fasting_Glucose" and (value < 20 or value > 500):
            issues.append(f"{param}: value {value} out of plausible range (20-500)")
        elif param == "WBC" and (value < 0.5 or value > 50):
            issues.append(f"{param}: value {value} out of plausible range (0.5-50)")
        
        validated[param] = value
    
    # Check for missing critical parameters
    missing = [p for p in REQUIRED_PARAMS if p not in validated]
    if missing:
        issues.append(f"Missing critical parameters: {', '.join(missing)}")
    
    # Determine confidence level
    if not validated:
        confidence = "low"
    elif missing or len(issues) > 3:
        confidence = "low"
    elif len(issues) > 0:
        confidence = "medium"
    else:
        confidence = "high"
    
    return {
        "validated": validated,
        "issues": issues,
        "confidence": confidence,
        "missing": missing
    }

# Compatibility alias
validate_data = validate_extracted

# Test
if __name__ == "__main__":
    test_data = {
        "Hemoglobin": 10.5,
        "Fasting_Glucose": 150.0,
        "WBC": -5  # Invalid
    }
    result = validate_extracted(test_data)
    print(f"Validated: {len(result['validated'])} params")
    print(f"Issues: {result['issues']}")
    print(f"Confidence: {result['confidence']}")
