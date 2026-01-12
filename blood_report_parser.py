import re

PARAMETER_MAP = {
    "hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "wbc_count": ["wbc", "total leukocyte count", "tlc"],
    "rbc_count": ["rbc", "red blood cell"],
    "platelets": ["platelet", "platelet count"],
    "sodium": ["sodium", "na+"],
    "potassium": ["potassium", "k+"],
    "bilirubin_total": ["total bilirubin", "bilirubin"],
    "sgot_ast": ["sgot", "ast"],
    "sgpt_alt": ["sgpt", "alt"],
    "alkaline_phosphatase": ["alkaline phosphatase", "alp"]
}

SEX_KEYWORDS = {
    "female": ["female", "f"],
    "male": ["male", "m"]
}

def extract_value(line):
    """
    Extracts the first reasonable numeric value from a line
    """
    match = re.search(r"\b\d+(\.\d+)?\b", line)
    if match:
        return float(match.group())
    return None

def parse_report(text):
    results = {}
    lines = text.split("\n")
    sex = None
    
    for line in lines:
        lower_line = line.lower()
        
        # Detect sex
        if sex is None:
            for sex_type, keywords in SEX_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in lower_line:
                        sex = sex_type
                        break
                if sex:
                    break
        
        # Extract parameters
        for param, aliases in PARAMETER_MAP.items():
            if param in results:
                continue
            for alias in aliases:
                if alias in lower_line:
                    value = extract_value(lower_line)
                    if value is not None:
                        results[param] = value
                    break
    
    return results, sex