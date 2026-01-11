def classify_parameter(value):
    if value < 0.33:
        return "Low"
    elif value < 0.66:
        return "Normal"
    else:
        return "High"

def interpret_row(row):
    return {k: classify_parameter(v) for k, v in row.items()}
