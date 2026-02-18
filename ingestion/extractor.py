import re
import json
import os

def extract_parameters(text):

    patterns = {
        "patient_name": r"patient\s*name\s*[:\-]?\s*(.*?)(?=\n|gender|sex|age|$)",
        "gender": r"(?:gender|sex)\s*[:\-]?\s*\b(male|female)\b",
        "age": r"age\s*[:\-]?\s*(\d+)",
        "hemoglobin": r"hemoglobin.*?([\d\.]+)",
        "wbc": r"wbc.*?([\d\.]+)",
        "rbc": r"rbc.*?([\d\.]+)",
        "platelets": r"platelets.*?([\d\.]+)",
        "glucose": r"glucose.*?([\d\.]+)",
        "hdl": r"hdl.*?([\d\.]+)",
        "ldl": r"ldl.*?([\d\.]+)",
        "cholesterol": r"cholesterol.*?([\d\.]+)",
        "triglycerides": r"triglycerides.*?([\d\.]+)",
        "neutrophils": r"neutrophils.*?([\d\.]+)",
        "tsh": r"tsh.*?([\d\.]+)",
        "t3": r"t3.*?([\d\.]+)",
        "t4": r"t4.*?([\d\.]+)",
        "creatinine": r"(?:creatinine|crea|cr).*?([\d\.]+)",
        "bilirubin": r"(?:bilirubin|bili|t\.bili).*?([\d\.]+)"
        
    }

    extracted = {}
    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if param not in ["patient_name", "gender"]:
                try:
                    extracted[param] = float(value)
                except ValueError:
                    extracted[param] = value
            else:
                extracted[param] = value

    missing_params = [p for p in patterns.keys() if p not in extracted]
    if missing_params:
        llm_data = _extract_missing_with_llm(text, missing_params)
        extracted.update(llm_data)

    return extracted

def _extract_missing_with_llm(text, missing_keys):
    prompt = f"""
    Act as a medical data extractor. Extract the following parameters from the text:
    {', '.join(missing_keys)}
    
    Return ONLY a raw JSON object. If a value is missing, use null.
    Text: {text}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return {k: v for k, v in json.loads(clean_json).items() if v is not None}
    except:
        return {}