from typing import Dict, Any, List

def generate_recommendations(summary: Dict[str, Any], patient_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate rule-based recommendations from synthesis summary.
    
    Args:
        summary: From findingssynthesizer (high_risks, abnormal_parameters, etc.)
        patient_context: {age, gender, name}
    
    Returns:
        List of recommendations [{disease, priority, tests, lifestyle, referral}, ...]
    """
    recs = []
    
    # High risk diseases → urgent recommendations
    high_risks = summary.get('high_risks', [])
    for disease in high_risks:
        if disease == 'diabetes_risk':
            recs.append({
                "disease": "Diabetes Risk",
                "priority": "high",
                "tests": ["A1C", "Fasting Glucose Retest", "Glucose Tolerance Test"],
                "lifestyle": ["Low-carb diet", "Regular exercise 30min/day", "Weight management"],
                "referral": "Endocrinologist consultation"
            })
        elif disease == 'cardiovascular_risk' or disease == 'cardio_risk':
            recs.append({
                "disease": "Cardiovascular Risk",
                "priority": "high",
                "tests": ["Lipid panel", "ECG", "Stress test"],
                "lifestyle": ["Heart-healthy diet", "Reduce sodium", "Quit smoking"],
                "referral": "Cardiologist consultation"
            })
        elif disease == 'anemia':
            recs.append({
                "disease": "Anemia",
                "priority": "high",
                "tests": ["Iron panel", "Ferritin", "Vitamin B12"],
                "lifestyle": ["Iron-rich foods (spinach, lentils)", "Vitamin C for absorption"],
                "referral": "Hematologist if severe"
            })
        elif disease == 'kidney_dysfunction':
            recs.append({
                "disease": "Kidney Dysfunction",
                "priority": "high",
                "tests": ["Renal function panel", "Ultrasound", "Urine analysis"],
                "lifestyle": ["Hydrate well", "Low-protein diet", "Avoid NSAIDs"],
                "referral": "Nephrologist consultation"
            })
        elif disease == 'liver_dysfunction':
            recs.append({
                "disease": "Liver Dysfunction",
                "priority": "high",
                "tests": ["Liver function panel", "Ultrasound", "Hepatitis screening"],
                "lifestyle": ["Avoid alcohol", "Limit fatty foods", "Weight loss if obese"],
                "referral": "Hepatologist consultation"
            })
        else:
            # Generic high risk
            recs.append({
                "disease": disease.replace('_', ' ').title(),
                "priority": "high",
                "tests": ["Specialist panel", "Follow-up labs"],
                "lifestyle": ["Healthy diet", "Regular exercise"],
                "referral": "Specialist consultation recommended"
            })
    
    # Moderate risks → routine follow-up
    moderate_risks = summary.get('moderate_risks', [])
    for disease in moderate_risks[:2]:  # Top 2 moderate
        recs.append({
            "disease": disease.replace('_', ' ').title(),
            "priority": "moderate",
            "tests": ["Routine monitoring", "Repeat labs in 3 months"],
            "lifestyle": ["Balanced diet", "Exercise", "Monitor symptoms"],
            "referral": "Primary care follow-up"
        })
    
    # If no risks detected
    if not recs:
        recs.append({
            "disease": "General Health Maintenance",
            "priority": "low",
            "tests": ["Annual checkup", "Routine screening"],
            "lifestyle": ["Balanced diet", "30min exercise daily", "Adequate sleep"],
            "referral": ""
        })
    
    return recs[:5]  # Max 5 recommendations

# Test
if __name__ == "__main__":
    test_summary = {
        "high_risks": ["diabetes_risk", "anemia"],
        "moderate_risks": ["hypertension"]
    }
    test_context = {"age": 45, "gender": "male", "name": "Test"}
    result = generate_recommendations(test_summary, test_context)
    print(f"Generated {len(result)} recommendations:")
    for r in result:
        print(f"  - {r['disease']} ({r['priority']})")
