
import re
def extract_parameters(text):
    patterns = {
        "Hemoglobin": r"HEMOGLOBIN\s*:\s*(\d+\.?\d*)",
        "Glucose": r"GLUCOSE\s*:\s*(\d+)",
        "Cholesterol": r"CHOLESTEROL\s*:\s*(\d+)",
        "WBC": r"TOTAL LEUKOCYTE COUNT\s*:\s*(\d+)",
        "Platelets": r"PLATELET COUNT\s*:\s*(\d+\.?\d*)"
    }
    data = {}
    for k,p in patterns.items():
        m = re.search(p, text, re.I)
        if m:
            data[k] = float(m.group(1))
    return data
