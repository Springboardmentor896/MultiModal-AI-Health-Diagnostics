import re

def extract_parameters(text):
    patterns = {
        "hemoglobin":r"hemoglobin.*?([\d\.]+)",
        "wbc": r"wbc.*?([\d\.]+)",
        "rbc": r"rbc.*?([\d\.]+)",
        "platelets": r"platelets.*?([\d\.]+)",
        "glucose": r"glucose.*?([\d\.]+)"
    }

    extracted = {}

    for parameters, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[parameters] = float(match.group(1))

    return extracted
