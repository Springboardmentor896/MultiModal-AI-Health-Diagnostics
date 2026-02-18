from utils.reference_ranges import REFERENCE_RANGES

def interpret(data):
    
    interpretation = {}

    for param, value in data.items():
        param_key = param.lower().replace("total ", "").strip()
        if param_key in ["patient_name", "gender", "age"] or param_key not in REFERENCE_RANGES:
            continue

        low, high = REFERENCE_RANGES[param_key]
        
        if value < low:
            status = "Low"
            desc = f"{param_key.title()} is below the normal range."
        elif value > high:
            status = "High"
            desc = f"{param_key.title()} is above the normal range."
        else:
            status = "Normal"
            desc = f"{param_key.title()} is within the healthy range."

        interpretation[param_key] = {
            "value": value,
            "status": status,
            "interpretation": desc,
            "range": f"{low} - {high}"
        }

    return interpretation