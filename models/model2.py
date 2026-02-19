import sys
import os
from datetime import datetime

# Add parent path to find the analysis module
sys.path.append(os.path.abspath('..'))

try:
    from analysis.medical_knowledge_base import COMPLEX_RULES
except ImportError:
    # Fallback if file not found (prevents crash)
    COMPLEX_RULES = []

class HealthAnalyst:
    def __init__(self):
        pass

    def _get_patient_status_map(self, patient_data):
        """
        Converts list of dicts into a simpler map for fast lookup.
        Example: {'Hemoglobin': 'Low', 'MCV': 'High', 'Glucose': 'Normal'}
        """
        status_map = {}
        for item in patient_data:
            # Normalize key to Title Case for consistent matching
            key = item['Parameter']
            
            # Map the specific flag from Interpreter to "High"/"Low"/"Normal"
            if "High" in item['Note']:
                status = "High"
            elif "Low" in item['Note']:
                status = "Low"
            else:
                status = "Normal"
            
            # handle case variations in parameter names
            # Map common variations to standard keys used in Knowledge Base
            key_lower = key.lower()
            if "hemoglobin" in key_lower and "mch" not in key_lower:
                status_map["Hemoglobin"] = status
            elif "mcv" in key_lower:
                status_map["MCV"] = status
            elif "wbc" in key_lower or "tlc" in key_lower:
                status_map["Total WBC Count"] = status
            elif "platelet" in key_lower:
                status_map["Platelet Count"] = status
            elif "neutrophil" in key_lower:
                status_map["Neutrophils"] = status
            elif "lymphocyte" in key_lower:
                status_map["Lymphocytes"] = status
            elif "glucose" in key_lower:
                status_map["Glucose"] = status
            elif "creatinine" in key_lower:
                status_map["Creatinine"] = status
                
        return status_map

    def generate_summary(self, patient_data, filename="Unknown"):
        """
        Generates a text summary using combinatorial logic.
        """
        status_map = self._get_patient_status_map(patient_data)
        summary_lines = []
        
        summary_lines.append(f"ANALYSIS REPORT FOR: {filename}")
        summary_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        summary_lines.append("-" * 40)

        # 1. Identify Potential Conditions (Combinatorial Logic)
        detected_conditions = []
        
        for rule in COMPLEX_RULES:
            condition_name = rule["condition"]
            criteria = rule["logic"] # List of tuples [('Hemoglobin', 'Low'), ...]
            
            match = True
            missing_data = False
            
            for param, required_status in criteria:
                if param not in status_map:
                    # If we don't have the data (e.g., Report didn't have MCV), we can't trigger the rule
                    match = False
                    missing_data = True
                    break
                
                if status_map[param] != required_status:
                    match = False
                    break
            
            if match:
                detected_conditions.append(rule)

        # 2. Build the Narrative
        if not detected_conditions:
            # Fallback check for single abnormalities if no complex patterns match
            abnormalities = [k for k, v in status_map.items() if v in ["High", "Low"]]
            
            if abnormalities:
                summary_lines.append(f"SUMMARY: Isolated abnormalities detected in {', '.join(abnormalities)}.")
                summary_lines.append("No specific complex syndrome pattern matched. Clinical correlation required.")
            else:
                summary_lines.append("SUMMARY: All extracted parameters are within normal physiological limits.")
        else:
            summary_lines.append(f"SUMMARY: Potential Patterns Detected ({len(detected_conditions)})")
            summary_lines.append("Based on the combination of values, the following conditions are indicated:\n")
            
            for cond in detected_conditions:
                summary_lines.append(f"DETECTED: {cond['condition']}")
                
                # List the evidence (Why did we trigger this?)
                evidence = []
                for p, s in cond['logic']:
                    # Find actual value from original data to display
                    # This is a bit inefficient search but safe for small lists
                    val_str = "N/A"
                    unit_str = ""
                    for original_item in patient_data:
                        if p.lower() in original_item['Parameter'].lower():
                            val_str = str(original_item['Value'])
                            unit_str = original_item['Unit']
                    evidence.append(f"{p} is {s} ({val_str} {unit_str})")
                
                summary_lines.append(f"  Evidence: {', '.join(evidence)}")
                summary_lines.append(f"  Recommendation: {cond['recommendation']}")
                summary_lines.append("") # Empty line for spacing

        return "\n".join(summary_lines)
