def calculate_confidence(data):
    TOTAL_EXPECTED = 14 
    clinical_keys = [
        k for k in data.keys() 
        if k not in ["patient_name", "gender", "age"]
    ]
    
    completeness = len(clinical_keys) / TOTAL_EXPECTED
    return round(completeness * 100, 2)