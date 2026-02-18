"""
Synthesizer Module
Combines results from all three models into final analysis
"""

from typing import Dict, Any, List


def synthesize_analysis(
    model1_result: Dict[str, Any],
    model2_result: Dict[str, Any],
    model3_result: Dict[str, Any],
    patient_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesize final analysis from all three models
    """
    
    # Get combined diseases from Model 3
    diseases = model3_result.get('combined_diseases', {})
    
    # Overall risk score
    overall_risk_score = model3_result.get('overall_risk_score', 50)
    
    # Determine risk level
    if overall_risk_score >= 70:
        risk_level = "HIGH"
    elif overall_risk_score >= 40:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"
    
    # Compile key findings
    key_findings = model1_result.get('findings', [])[:5]  # Top 5 findings
    
    # Generate recommendations
    recommendations = generate_recommendations(diseases, key_findings, patient_info)
    
    # Compile final analysis
    final_analysis = {
        'overall_risk_score': overall_risk_score,
        'risk_level': risk_level,
        'diseases': diseases,
        'key_findings': key_findings,
        'recommendations': recommendations,
        'model1_result': model1_result,
        'model2_result': model2_result,
        'model3_result': model3_result,
        'confidence_score': 90,
        'patient_info': patient_info
    }
    
    return final_analysis


def generate_recommendations(
    diseases: Dict[str, Any],
    findings: List[str],
    patient_info: Dict[str, Any]
) -> List[str]:
    """
    Generate personalized recommendations based on analysis
    """
    
    recommendations = []
    
    # Check for high-risk diseases
    high_risk_diseases = [d for d, data in diseases.items() if data['risk_percentage'] >= 60]
    
    if high_risk_diseases:
        recommendations.append(
            f"🚨 URGENT: Consult a healthcare provider immediately regarding: {', '.join(high_risk_diseases)}"
        )
    
    # Specific recommendations based on diseases
    if 'Anemia' in diseases:
        recommendations.append("Consider iron supplementation and iron-rich diet (spinach, red meat, lentils)")
        recommendations.append("Schedule follow-up complete blood count (CBC) test")
    
    if 'Diabetes' in diseases or 'Pre-diabetes' in diseases:
        recommendations.append("Monitor blood glucose regularly")
        recommendations.append("Reduce refined carbohydrates and sugar intake")
        recommendations.append("Increase physical activity (30 min daily)")
    
    if 'Infection' in diseases:
        recommendations.append("Consult doctor for possible antibiotic treatment")
        recommendations.append("Stay hydrated and get adequate rest")
    
    if 'Kidney Disease' in diseases:
        recommendations.append("Reduce sodium intake and stay well-hydrated")
        recommendations.append("Monitor blood pressure regularly")
        recommendations.append("Schedule kidney function test (eGFR)")
    
    if 'Liver Disease' in diseases:
        recommendations.append("Avoid alcohol consumption")
        recommendations.append("Consider hepatitis screening if not done")
    
    if 'Heart Disease Risk' in diseases:
        recommendations.append("Schedule lipid profile and cardiac evaluation")
        recommendations.append("Adopt heart-healthy diet (low saturated fat)")
        recommendations.append("Consider starting cardiovascular exercise program")
    
    # General recommendations
    if not recommendations:
        recommendations.append("✅ Your lab results appear within normal ranges")
        recommendations.append("Continue maintaining healthy lifestyle habits")
        recommendations.append("Schedule routine checkup as per your doctor's advice")
    
    recommendations.append("⚕️ Always consult a licensed healthcare professional before making any medical decisions")
    
    return recommendations
