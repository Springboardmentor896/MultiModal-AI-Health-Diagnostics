TARGET_MAP = {
    # --- CBC ---
    "hemoglobin": "Hemoglobin",
    "haemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "total wbc": "Total WBC",
    "total leukocyte": "Total WBC",
    "tlc": "Total WBC",
    "platelet": "Platelet Count",
    "plt": "Platelet Count",
    "neutrophils": "Neutrophils",
    "lymphocytes": "Lymphocytes",
    "rbc": "RBC Count",
    "red blood cell": "RBC Count",
    "mcv": "MCV",
    "pcv": "PCV",
    
    # --- DIABETES ---
    "glucose": "Glucose",
    "fasting": "Glucose",
    "fbs": "Glucose",
    "blood sugar": "Glucose",
    
    # --- KIDNEY ---
    "blood urea": "Blood Urea",
    "urea": "Blood Urea",
    "bun": "Blood Urea",
    "creatinine": "Creatinine",
    "s.creatinine": "Creatinine",
    
    # --- LIVER ---
    "total bilirubin": "Total Bilirubin",
    "bilirubin total": "Total Bilirubin",
    "direct bilirubin": "Direct Bilirubin",
    "indirect bilirubin": "Indirect Bilirubin",
    "sgot": "SGOT (AST)",
    "ast": "SGOT (AST)",
    "sgpt": "SGPT (ALT)",
    "alt": "SGPT (ALT)",
    "alkaline phosphatase": "Alkaline Phosphatase",
    "alp": "Alkaline Phosphatase",
    
    # --- LIPID (If present) ---
    "cholesterol": "Total Cholesterol",
    "triglycerides": "Triglycerides",
    "hdl": "HDL Cholesterol",
    "ldl": "LDL Cholesterol"
}

def standardize_data(extracted_list):
    standardized = []
    
    for item in extracted_list:
        raw_name = item['Parameter'].lower()
        
        standard_name = item['Parameter']
        
        for key, val in TARGET_MAP.items():
            if key in raw_name:
                standard_name = val
                break
        
        unit = item['Unit'].lower()
        if "gm" in unit: unit = "g/dL"
        if "cumm" in unit: unit = "/cumm"
        if "mg" in unit and "dl" in unit: unit = "mg/dL"
        if "iu" in unit: unit = "U/L"
        
        standardized.append({
            "Parameter": standard_name,
            "Value": item['Value'],
            "Unit": unit,
            "Range": item['Range'] 
        })
        
    return standardized
