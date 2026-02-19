import re

def extract_patient_info(ocr_text):
    """
    Parses the raw OCR text to find Patient Demographics.
    Returns a dictionary matching the PATIENT_PROFILE structure used in analysis.
    """
    profile = {
        "name": "Unknown",
        "age": 35,
        "gender": "Male",
        "is_pregnant": False
    }

    name_match = re.search(r"Patient Name:\s*(.*)", ocr_text, re.IGNORECASE)
    if name_match:
        profile['name'] = name_match.group(1).strip()

    combined_match = re.search(r"Age/Gender:\s*(\d+).*?/\s*(\w+)", ocr_text, re.IGNORECASE)
    
    if combined_match:
        try:
            profile['age'] = int(combined_match.group(1))
            profile['gender'] = combined_match.group(2).strip().capitalize()
        except:
            pass
    else:
        age_match = re.search(r"Age:\s*(\d+)", ocr_text, re.IGNORECASE)
        if age_match: 
            profile['age'] = int(age_match.group(1))
        
        sex_match = re.search(r"(Gender|Sex):\s*(\w+)", ocr_text, re.IGNORECASE)
        if sex_match: 
            profile['gender'] = sex_match.group(2).strip().capitalize()

    if "pregnancy: positive" in ocr_text.lower():
        profile['is_pregnant'] = True
    elif "status: pregnant" in ocr_text.lower():
        profile['is_pregnant'] = True
    
    return profile
