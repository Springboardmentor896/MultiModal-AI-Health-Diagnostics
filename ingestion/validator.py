def validate_data(extracted_data):
    if not extracted_data:
        return {}

    validated = {}
    SANITY_LIMITS = {
        "age": (0, 120),
        "hemoglobin": (2.0, 25.0),    
        "wbc": (100, 100000),        
        "rbc": (1.0, 10.0),           
        "platelets": (5000, 1000000),
        "neutrophils": (0, 100),
        "glucose": (20.0, 1000.0), 
        "cholesterol": (50, 600),    
        "hdl": (5, 150),             
        "ldl": (10, 400),             
        "triglycerides": (10, 1500),
        "creatinine": (0.1, 20.0),   
        "bilirubin": (0.1, 50.0),
        "tsh": (0.01, 150.0),        
        "t3": (10, 800),              
        "t4": (0.1, 30.0)            
    }

    for key, value in extracted_data.items():
        if key in ["patient_name", "gender"]:
            validated[key] = str(value).strip() if value else "Unknown"
            continue

        try:
            num_value = float(value)
            
            if key in SANITY_LIMITS:
                min_val, max_val = SANITY_LIMITS[key]
                if min_val <= num_value <= max_val:
                    validated[key] = num_value
                else:
                    print(f" Filtered: {key} ({num_value}) is biologically improbable.")
            else:
                validated[key] = num_value
        
        except (ValueError, TypeError):
            continue

    return validated