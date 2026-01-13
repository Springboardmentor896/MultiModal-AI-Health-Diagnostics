import re
SAFETY_LIMITS = {
    "Hemoglobin": (2.0, 250.0),
    "Total WBC Count": (500, 50000),
    "Platelet Count": (10000, 1000000),
    "Neutrophils": (0, 100),
    "Lymphocytes": (0, 100),
    "Packed Cell Volume": (10, 70),
    "PCV": (10, 70),
    "Glucose": (20, 600),
    "Creatinine": (0.1, 15.0),
    "RBC": (1.0, 10.0),
    "MCV": (50, 120),
    "MCH": (15, 40),
    "MCHC": (20, 45)
}

NOISE_WORDS = [
    "method", "calculated", "colorimetric", "photometry", "electric", 
    "impedance", "flow", "cytometry", "fcm", "microscopy", "estimation", 
    "blood", "count", "estimation", "test", "result", "units", "range"
]

def clean_parameter_name(raw_name):
    name = re.sub(r"\(.*?\)", "", raw_name)
    
    for word in NOISE_WORDS:
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        name = pattern.sub("", name)
        
    return name.strip(" :.-").title()

def smart_parse_and_correct(ocr_text):
    extracted_data = []
    lines = ocr_text.split('\n')
    
    range_pattern = r"(?P<range>[\(\[]?\s*(?P<low>[<>≤≥]?\s*\d+(?:\.\d+)?)\s*[-–to]\s*(?P<high>\d+(?:\.\d+)?)\s*[\)\]]?)"
    
    value_pattern = r"(?P<value>\d+(?:\.\d+)?)"

    for line in lines:
        line = line.strip()
        if len(line) < 10: continue

        range_match = re.search(range_pattern, line)
        
        if range_match:
            r_start, r_end = range_match.span()
            range_str = range_match.group("range")
            
            text_prefix = line[:r_start].strip()
            text_suffix = line[r_end:].strip()
            
            val_matches = list(re.finditer(value_pattern, text_prefix))
            
            if val_matches:
                val_match = val_matches[-1]
                val_start, val_end = val_match.span()
                raw_val = float(val_match.group("value"))
                
                raw_unit = ""
                
                if len(text_suffix) > 0 and len(text_suffix) < 15: 
                    raw_unit = text_suffix
                
                if not raw_unit:
                    potential_unit = text_prefix[val_end:].strip()
                    potential_unit = re.sub(r"(?i)(female|male|adults|child|ref)\s*[:\-]?", "", potential_unit)
                    raw_unit = potential_unit.strip()

                raw_name_segment = text_prefix[:val_start]
                clean_name = clean_parameter_name(raw_name_segment)

                if not clean_name or len(clean_name) < 2: continue

                final_val = raw_val
                status = "Raw"
                
                matched_key = None
                for key in SAFETY_LIMITS:
                    if key.lower() in clean_name.lower():
                        matched_key = key
                        break
                
                if matched_key:
                    low_lim, high_lim = SAFETY_LIMITS[matched_key]
                    
                    if final_val > high_lim:
                        if (final_val / 10) <= high_lim and (final_val / 10) >= low_lim:
                            final_val /= 10
                            status = "Corrected (Decimal)"
                        elif (final_val / 100) <= high_lim and (final_val / 100) >= low_lim:
                            final_val /= 100
                            status = "Corrected (Decimal)"
                        else:
                            status = "Flagged (Out of Range)"
                            final_val = None

                extracted_data.append({
                    "parameter_name": clean_name,
                    "extracted_value": final_val,
                    "extracted_unit": raw_unit,
                    "extracted_range": range_str,
                    "extraction_status": status
                })

    return extracted_data
