
def interpret(data):
    ref = {
        "Hemoglobin": (12,16),
        "Glucose": (70,110),
        "Cholesterol": (0,200),
        "WBC": (4000,11000),
        "Platelets": (1.5,4.5)
    }
    result = {}
    for k,v in data.items():
        lo,hi = ref.get(k,(0,9999))
        if v < lo: s="Low"
        elif v > hi: s="High"
        else: s="Normal"
        result[k] = {"value":v,"status":s}
    return result
