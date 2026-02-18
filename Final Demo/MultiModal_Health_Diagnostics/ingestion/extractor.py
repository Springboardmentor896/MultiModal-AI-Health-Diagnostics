"""
Extractor Module
Extracts structured lab data from raw text using regex patterns
"""

import re


def extract_lab_data(text):
    """
    Extract lab parameters from text using regex patterns
    
    Args:
        text: Raw text from parsed document
    
    Returns:
        dict: Extracted lab parameters with numeric values
    """
    lab_data = {}
    
    # Normalize text (handle various formats)
    text = text.replace(',', '')  # Remove commas from numbers
    text_lower = text.lower()
    
    # Hemoglobin patterns - IMPROVED
    hb_patterns = [
        r'hemoglobin\s*\(hb\)\s*(\d+\.?\d*)',  # "Hemoglobin (Hb) 12.5"
        r'hemoglobin[:\s]+(?:hb[:\s]+)?(\d+\.?\d*)',
        r'\bhb[:\s]+(\d+\.?\d*)',
        r'haemoglobin[:\s]+(\d+\.?\d*)'
    ]
    for pattern in hb_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['hemoglobin'] = float(match.group(1))
            break
    
    # RBC Count patterns
    rbc_patterns = [
        r'total\s+rbc\s+count[:\s]+(\d+\.?\d*)',
        r'rbc[:\s]+(?:count[:\s]+)?(\d+\.?\d*)',
        r'red\s+blood\s+cell[:\s]+(\d+\.?\d*)'
    ]
    for pattern in rbc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['rbc'] = float(match.group(1))
            break
    
    # WBC Count patterns
    wbc_patterns = [
        r'total\s+wbc\s+count[:\s]+(\d+)',
        r'wbc[:\s]+(?:count[:\s]+)?(\d+)',
        r'white\s+blood\s+cell[:\s]+(\d+)',
        r'total\s+leukocyte\s+count[:\s]+(\d+\.?\d*)'
    ]
    for pattern in wbc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            wbc_value = float(match.group(1))
            # Handle different units (if in thousands)
            if wbc_value < 100:
                wbc_value *= 1000
            lab_data['wbc'] = int(wbc_value)
            break
    
    # Platelet Count patterns
    platelet_patterns = [
        r'platelet\s+count[:\s]+(\d+)',
        r'platelet[:\s]+(?:count[:\s]+)?(\d+)',
        r'platelets[:\s]+(\d+)',
        r'plt[:\s]+(\d+)'
    ]
    for pattern in platelet_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['platelets'] = int(match.group(1))
            break
    
    # PCV / Hematocrit patterns - IMPROVED
    pcv_patterns = [
        r'packed\s+cell\s+volume\s*\(pcv\)\s*(\d+\.?\d*)',  # "Packed Cell Volume (PCV) 57.5"
        r'pcv[:\s]+(\d+\.?\d*)',
        r'packed\s+cell\s+volume[:\s]+(\d+\.?\d*)',
        r'hematocrit[:\s]+(\d+\.?\d*)',
        r'haematocrit[:\s]+(\d+\.?\d*)'
    ]
    for pattern in pcv_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['pcv'] = float(match.group(1))
            break
    
    # MCV patterns - IMPROVED
    mcv_patterns = [
        r'mean\s+corpuscular\s+volume\s*\(mcv\)\s*(\d+\.?\d*)',  # "Mean Corpuscular Volume (MCV) 87.75"
        r'mcv[:\s]+(\d+\.?\d*)',
        r'mean\s+corpuscular\s+volume[:\s]+(\d+\.?\d*)'
    ]
    for pattern in mcv_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['mcv'] = float(match.group(1))
            break
    
    # MCH patterns - IMPROVED
    mch_patterns = [
        r'\bmch\s+(\d+\.?\d*)',  # Word boundary to avoid matching MCHC
        r'mch[:\s]+(\d+\.?\d*)',
        r'mean\s+corpuscular\s+h[ae]?moglobin[:\s]+(?!concentration)(\d+\.?\d*)'
    ]
    for pattern in mch_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['mch'] = float(match.group(1))
            break
    
    # MCHC patterns - IMPROVED
    mchc_patterns = [
        r'mchc\s+(\d+\.?\d*)',
        r'mchc[:\s]+(\d+\.?\d*)',
        r'mean\s+corpuscular\s+h[ae]?moglobin\s+concentration[:\s]+(\d+\.?\d*)'
    ]
    for pattern in mchc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['mchc'] = float(match.group(1))
            break
    
    # RDW patterns
    rdw_patterns = [
        r'rdw[:\s]+(\d+\.?\d*)',
        r'red\s+cell\s+distribution\s+width[:\s]+(\d+\.?\d*)'
    ]
    for pattern in rdw_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['rdw'] = float(match.group(1))
            break
    
    # Neutrophils patterns
    neutrophil_patterns = [
        r'neutrophils?[:\s]+(\d+\.?\d*)',
        r'neutros?[:\s]+(\d+\.?\d*)',
        r'polymorphs?[:\s]+(\d+\.?\d*)'
    ]
    for pattern in neutrophil_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['neutrophils'] = float(match.group(1))
            break
    
    # Lymphocytes patterns
    lymphocyte_patterns = [
        r'lymphocytes?[:\s]+(\d+\.?\d*)',
        r'lymphos?[:\s]+(\d+\.?\d*)'
    ]
    for pattern in lymphocyte_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['lymphocytes'] = float(match.group(1))
            break
    
    # Monocytes patterns
    monocyte_patterns = [
        r'monocytes?[:\s]+(\d+\.?\d*)',
        r'monos?[:\s]+(\d+\.?\d*)'
    ]
    for pattern in monocyte_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['monocytes'] = float(match.group(1))
            break
    
    # Eosinophils patterns
    eosinophil_patterns = [
        r'eosinophils?[:\s]+(\d+\.?\d*)',
        r'eos[:\s]+(\d+\.?\d*)'
    ]
    for pattern in eosinophil_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['eosinophils'] = float(match.group(1))
            break
    
    # Basophils patterns
    basophil_patterns = [
        r'basophils?[:\s]+(\d+\.?\d*)',
        r'basos?[:\s]+(\d+\.?\d*)'
    ]
    for pattern in basophil_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['basophils'] = float(match.group(1))
            break
    
    # ESR patterns
    esr_patterns = [
        r'esr[:\s]+(\d+\.?\d*)',
        r'erythrocyte\s+sedimentation\s+rate[:\s]+(\d+\.?\d*)'
    ]
    for pattern in esr_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lab_data['esr'] = float(match.group(1))
            break
    
    return lab_data


def validate_lab_data(lab_data):
    """
    Validate extracted lab data for reasonable ranges
    
    Args:
        lab_data: Dictionary of extracted lab parameters
    
    Returns:
        dict: Validated lab data with warnings
    """
    warnings = []
    
    # Define reasonable ranges
    ranges = {
        'hemoglobin': (5.0, 20.0),
        'rbc': (2.0, 8.0),
        'wbc': (1000, 30000),
        'platelets': (20000, 1000000),
        'pcv': (20.0, 70.0),
        'mcv': (60.0, 120.0),
        'mch': (20.0, 40.0),
        'mchc': (28.0, 38.0),
        'neutrophils': (0.0, 100.0),
        'lymphocytes': (0.0, 100.0)
    }
    
    for param, value in lab_data.items():
        if param in ranges:
            min_val, max_val = ranges[param]
            if value < min_val or value > max_val:
                warnings.append(f"{param} value {value} is outside expected range ({min_val}-{max_val})")
    
    return {
        'data': lab_data,
        'warnings': warnings,
        'is_valid': len(warnings) == 0
    }
