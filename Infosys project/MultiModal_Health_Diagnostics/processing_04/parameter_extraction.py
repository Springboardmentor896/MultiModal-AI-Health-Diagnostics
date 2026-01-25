import re

PATTERNS = {
    "hemoglobin": r"Hemoglobin[:\s]+([\d.]+)",
    "rbc": r"RBC[:\s]+([\d.]+)",
    "wbc": r"WBC[:\s]+([\d.]+)",
    "platelets": r"Platelets[:\s]+([\d.]+)",
    "glucose": r"Glucose[:\s]+([\d.]+)",
    "bilirubin": r"Bilirubin[:\s]+([\d.]+)",
    "cholesterol": r"Cholesterol[:\s]+([\d.]+)"
}

def extract_parameters(text):
    """
    Input: raw text from PDF / Image
    Output: numeric parameter values
    """
    extracted = {}
    for param, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[param] = float(match.group(1))
    return extracted
