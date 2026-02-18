
import re


def extract_parameters(text):
    patterns = {
        "Hemoglobin": r"HEMOGLOBIN\s*:\s*(\d+\.?\d*)",
        "Glucose": r"GLUCOSE\s*:\s*(\d+)",
        "Cholesterol": r"CHOLESTEROL\s*:\s*(\d+)",
        "WBC": r"TOTAL LEUKOCYTE COUNT\s*:\s*(\d+)",
        # Capture platelet value with optional lakh wording
        "Platelets": r"PLATELET COUNT\s*:\s*(\d+\.?\d*)\s*(lakhs?|lacs?|lakh|lac)?"
    }

    data = {}
    for k, p in patterns.items():
        m = re.search(p, text, re.I)
        if m:
            val = float(m.group(1))
            if k == "Platelets":
                unit_word = m.group(2).lower() if m.lastindex and m.lastindex >= 2 and m.group(2) else ""
                if unit_word in {"lakh", "lakhs", "lac", "lacs"}:
                    platelet_lakh = val
                else:
                    # If absolute count, convert to lakhs/cumm
                    if val >= 20_000:
                        platelet_lakh = val / 100_000.0
                    else:
                        platelet_lakh = val
                        if platelet_lakh > 10:
                            platelet_lakh = platelet_lakh / 10.0
                        if platelet_lakh > 10:
                            platelet_lakh = platelet_lakh / 10.0
                data[k] = platelet_lakh
            else:
                data[k] = val
    return data
