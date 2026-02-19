import json
import os

def load_ranges(json_path):
    if not os.path.exists(json_path):
        return {}
    with open(json_path, 'r') as f:
        return json.load(f)

def interpret_results(standardized_data, ref_ranges_path):
    ref_ranges = load_ranges(ref_ranges_path)
    final_report = []

    for item in standardized_data:
        key = item['parameter_key']
        val = item['value']
        
        interpretation = "Normal"
        flag = "Normal"
        
        if key in ref_ranges:
            ref = ref_ranges[key]
            min_ref = ref['min']
            max_ref = ref['max']
            
            if val < min_ref:
                interpretation = f"Low (Ref: {min_ref}-{max_ref})"
                flag = "Abnormal"
            elif val > max_ref:
                interpretation = f"High (Ref: {min_ref}-{max_ref})"
                flag = "Abnormal"
        else:
            interpretation = "Reference range unavailable"
        
        final_report.append({
            "Parameter": item['original_name'],
            "Value": val,
            "Unit": item['unit'],
            "Status": flag,
            "Note": interpretation
        })
        
    return final_report
