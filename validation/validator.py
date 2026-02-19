TARGET_UNITS = {
    "hemoglobin": "g/dl",
    "total wbc count": "/cumm",
    "platelet count": "/cumm",
    "glucose": "mg/dl",
    "creatinine": "mg/dl",
    "rbc": "mil/cumm",
    "mcv": "fl"
}

def standardize_units(extracted_list):
    standardized_data = []

    for item in extracted_list:
        if item['extracted_value'] is None:
            continue

        param = item['parameter_name'].lower()
        val = item['extracted_value']
        unit = str(item['extracted_unit']).lower()
        
        
        if "hemoglobin" in param:
            if "gms" in unit or "%" in unit:
                unit = "g/dl" 
            elif "g/l" in unit: 
                val = val / 10
                unit = "g/dl"

        if "wbc" in param or "platelet" in param:
            if "10^3" in unit or "k/ul" in unit:
                 if val < 500: 
                     val = val * 1000
            unit = "/cumm"

        if "glucose" in param and "mol" in unit:
            val = val * 18
            unit = "mg/dl"
            
        if "creatinine" in param and "mol" in unit:
            val = val / 88.4
            unit = "mg/dl"

        matched_key = next((k for k in TARGET_UNITS if k in param), param)

        standardized_data.append({
            "parameter_key": matched_key,
            "original_name": item['parameter_name'],
            "value": round(val, 2),
            "unit": TARGET_UNITS.get(matched_key, unit),
            "original_unit": item['extracted_unit'],
            "status": "Standardized"
        })
        
    return standardized_data
