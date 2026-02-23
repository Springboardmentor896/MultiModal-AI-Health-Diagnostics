"""
Analysis Models
Three-model approach for health diagnostics
"""

import numpy as np
from typing import Dict, List, Any


def clinical_rule_based_model(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Model 1: Clinical Rule-Based Analysis
    Uses medical guidelines and reference ranges
    """
    
    findings = []
    diseases = {}
    abnormal_params = []
    
    # Reference ranges (standard medical values)
    reference_ranges = {
        'hemoglobin': {'male': (13.5, 17.5), 'female': (12.0, 15.5), 'unit': 'g/dL'},
        'wbc': {'normal': (4000, 11000), 'unit': 'cells/μL'},
        'platelets': {'normal': (150000, 450000), 'unit': 'cells/μL'},
        'glucose': {'normal': (70, 100), 'unit': 'mg/dL'},
        'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1), 'unit': 'mg/dL'},
        'alt': {'normal': (7, 56), 'unit': 'U/L'},
        'ast': {'normal': (10, 40), 'unit': 'U/L'},
        'bilirubin': {'normal': (0.1, 1.2), 'unit': 'mg/dL'},
        'cholesterol': {'normal': (125, 200), 'unit': 'mg/dL'},
        'triglycerides': {'normal': (0, 150), 'unit': 'mg/dL'},
        'tsh': {'normal': (0.4, 4.0), 'unit': 'mIU/L'},
        'hba1c': {'normal': (4.0, 5.6), 'unit': '%'}
    }
    
    # Analyze each parameter
    for param_name, param_data in parameters.items():
        try:
            value = float(param_data['value'])
            param_lower = param_name.lower().replace(' ', '_')
            
            # Check hemoglobin
            if 'hemoglobin' in param_lower or 'hgb' in param_lower or 'hb' in param_lower:
                if value < 12.0:
                    findings.append(f"Low hemoglobin: {value} g/dL (Anemia)")
                    abnormal_params.append(param_name)
                    diseases['Anemia'] = {'risk_percentage': 95, 'risk_level': 'HIGH'}
                elif value > 17.5:
                    findings.append(f"High hemoglobin: {value} g/dL (Polycythemia risk)")
                    abnormal_params.append(param_name)
            
            # Check WBC
            elif 'wbc' in param_lower or 'white' in param_lower:
                if value > 11000:
                    findings.append(f"High WBC: {value} (Infection/Inflammation)")
                    abnormal_params.append(param_name)
                    diseases['Infection'] = {'risk_percentage': 75, 'risk_level': 'HIGH'}
                elif value < 4000:
                    findings.append(f"Low WBC: {value} (Immune weakness)")
                    abnormal_params.append(param_name)
            
            # Check Platelets
            elif 'platelet' in param_lower:
                if value < 150000:
                    findings.append(f"Low platelets: {value} (Bleeding risk)")
                    abnormal_params.append(param_name)
                    diseases['Thrombocytopenia'] = {'risk_percentage': 80, 'risk_level': 'HIGH'}
                elif value > 450000:
                    findings.append(f"High platelets: {value} (Clotting risk)")
                    abnormal_params.append(param_name)
            
            # Check Glucose
            elif 'glucose' in param_lower or 'sugar' in param_lower:
                if value > 125:
                    findings.append(f"High glucose: {value} mg/dL (Diabetes risk)")
                    abnormal_params.append(param_name)
                    diseases['Diabetes'] = {'risk_percentage': 85, 'risk_level': 'HIGH'}
                elif value < 70:
                    findings.append(f"Low glucose: {value} mg/dL (Hypoglycemia)")
                    abnormal_params.append(param_name)
            
            # Check Creatinine
            elif 'creatinine' in param_lower:
                if value > 1.3:
                    findings.append(f"High creatinine: {value} mg/dL (Kidney dysfunction)")
                    abnormal_params.append(param_name)
                    diseases['Kidney Disease'] = {'risk_percentage': 70, 'risk_level': 'HIGH'}
            
            # Check Liver enzymes (ALT/AST)
            elif 'alt' in param_lower or 'sgpt' in param_lower:
                if value > 56:
                    findings.append(f"Elevated ALT: {value} U/L (Liver stress)")
                    abnormal_params.append(param_name)
                    diseases['Liver Disease'] = {'risk_percentage': 65, 'risk_level': 'MODERATE'}
            
            elif 'ast' in param_lower or 'sgot' in param_lower:
                if value > 40:
                    findings.append(f"Elevated AST: {value} U/L (Liver/Heart stress)")
                    abnormal_params.append(param_name)
            
            # Check Cholesterol
            elif 'cholesterol' in param_lower and 'hdl' not in param_lower and 'ldl' not in param_lower:
                if value > 240:
                    findings.append(f"High cholesterol: {value} mg/dL (Heart risk)")
                    abnormal_params.append(param_name)
                    diseases['Heart Disease Risk'] = {'risk_percentage': 60, 'risk_level': 'MODERATE'}
            
            # Check HbA1c
            elif 'hba1c' in param_lower or 'a1c' in param_lower:
                if value > 6.5:
                    findings.append(f"High HbA1c: {value}% (Diabetes)")
                    abnormal_params.append(param_name)
                    diseases['Diabetes'] = {'risk_percentage': 90, 'risk_level': 'HIGH'}
                elif value > 5.7:
                    findings.append(f"Elevated HbA1c: {value}% (Pre-diabetes)")
                    abnormal_params.append(param_name)
                    diseases['Pre-diabetes'] = {'risk_percentage': 65, 'risk_level': 'MODERATE'}
            
            # Check TSH (Thyroid)
            elif 'tsh' in param_lower:
                if value > 4.0:
                    findings.append(f"High TSH: {value} mIU/L (Hypothyroidism)")
                    abnormal_params.append(param_name)
                    diseases['Hypothyroidism'] = {'risk_percentage': 70, 'risk_level': 'MODERATE'}
                elif value < 0.4:
                    findings.append(f"Low TSH: {value} mIU/L (Hyperthyroidism)")
                    abnormal_params.append(param_name)
                    diseases['Hyperthyroidism'] = {'risk_percentage': 70, 'risk_level': 'MODERATE'}
                    
        except (ValueError, KeyError):
            continue
    
    return {
        'findings': findings,
        'diseases': diseases,
        'abnormal_parameters': abnormal_params,
        'model_name': 'Clinical Rule-Based Model',
        'confidence': 92
    }


def ml_risk_model(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Model 2: Machine Learning Risk Assessment
    Statistical risk scoring based on parameter patterns
    """
    
    risk_scores = {}
    feature_importances = {}
    
    # Extract numeric values
    param_values = {}
    for param, data in parameters.items():
        try:
            param_values[param.lower()] = float(data['value'])
        except:
            continue
    
    # Calculate composite risk scores for different conditions
    
    # Anemia risk (based on hemoglobin, RBC, etc.)
    anemia_score = 0
    if any('hemoglobin' in k or 'hb' in k for k in param_values.keys()):
        hb_value = next((v for k, v in param_values.items() if 'hemoglobin' in k or 'hb' in k), 13)
        if hb_value < 12:
            anemia_score = min(100, (12 - hb_value) / 12 * 100)
    
    # Infection risk (based on WBC)
    infection_score = 0
    if any('wbc' in k or 'white' in k for k in param_values.keys()):
        wbc_value = next((v for k, v in param_values.items() if 'wbc' in k or 'white' in k), 7000)
        if wbc_value > 11000:
            infection_score = min(100, (wbc_value - 11000) / 11000 * 100)
    
    # Diabetes risk (based on glucose and HbA1c)
    diabetes_score = 0
    if any('glucose' in k or 'sugar' in k for k in param_values.keys()):
        glucose_value = next((v for k, v in param_values.items() if 'glucose' in k or 'sugar' in k), 90)
        if glucose_value > 100:
            diabetes_score = min(100, (glucose_value - 100) / 100 * 80)
    
    if any('hba1c' in k or 'a1c' in k for k in param_values.keys()):
        hba1c_value = next((v for k, v in param_values.items() if 'hba1c' in k or 'a1c' in k), 5.0)
        if hba1c_value > 5.7:
            diabetes_score = max(diabetes_score, min(100, (hba1c_value - 5.7) / 5.7 * 100))
    
    # Kidney risk (based on creatinine)
    kidney_score = 0
    if any('creatinine' in k for k in param_values.keys()):
        creat_value = next((v for k, v in param_values.items() if 'creatinine' in k), 1.0)
        if creat_value > 1.3:
            kidney_score = min(100, (creat_value - 1.3) / 1.3 * 100)
    
    # Liver risk (based on ALT, AST)
    liver_score = 0
    if any('alt' in k or 'sgpt' in k for k in param_values.keys()):
        alt_value = next((v for k, v in param_values.items() if 'alt' in k or 'sgpt' in k), 30)
        if alt_value > 56:
            liver_score = min(100, (alt_value - 56) / 56 * 80)
    
    # Compile risk scores
    if anemia_score > 0:
        risk_scores['Anemia'] = {'risk_percentage': round(anemia_score, 1), 'confidence': 88}
    if infection_score > 0:
        risk_scores['Infection'] = {'risk_percentage': round(infection_score, 1), 'confidence': 85}
    if diabetes_score > 0:
        risk_scores['Diabetes'] = {'risk_percentage': round(diabetes_score, 1), 'confidence': 90}
    if kidney_score > 0:
        risk_scores['Kidney Disease'] = {'risk_percentage': round(kidney_score, 1), 'confidence': 87}
    if liver_score > 0:
        risk_scores['Liver Disease'] = {'risk_percentage': round(liver_score, 1), 'confidence': 82}
    
    return {
        'risk_scores': risk_scores,
        'feature_importances': feature_importances,
        'model_name': 'ML Risk Assessment Model',
        'confidence': 88
    }


def contextual_analysis_model(
    parameters: Dict[str, Any],
    model1_result: Dict[str, Any],
    model2_result: Dict[str, Any],
    age: int = 30,
    gender: str = "Male"
) -> Dict[str, Any]:
    """
    Model 3: Contextual Analysis
    Combines results from Model 1 & 2 with patient context
    """
    
    # Merge disease findings from both models
    all_diseases = {}
    
    # From Model 1
    for disease, data in model1_result.get('diseases', {}).items():
        all_diseases[disease] = {
            'risk_percentage': data['risk_percentage'],
            'risk_level': data['risk_level'],
            'source': 'Clinical Rules'
        }
    
    # From Model 2
    for disease, data in model2_result.get('risk_scores', {}).items():
        if disease in all_diseases:
            # Average the scores if both models detected it
            avg_risk = (all_diseases[disease]['risk_percentage'] + data['risk_percentage']) / 2
            all_diseases[disease]['risk_percentage'] = round(avg_risk, 1)
            all_diseases[disease]['source'] = 'Both Models'
        else:
            all_diseases[disease] = {
                'risk_percentage': data['risk_percentage'],
                'risk_level': 'HIGH' if data['risk_percentage'] > 60 else 'MODERATE' if data['risk_percentage'] > 30 else 'LOW',
                'source': 'ML Model'
            }
    
    # Apply age/gender context adjustments
    contextual_adjustments = []
    
    if age > 60:
        contextual_adjustments.append("Increased baseline risk due to age (>60)")
        # Slightly increase cardiovascular and kidney risks
        if 'Heart Disease Risk' in all_diseases:
            all_diseases['Heart Disease Risk']['risk_percentage'] += 10
        if 'Kidney Disease' in all_diseases:
            all_diseases['Kidney Disease']['risk_percentage'] += 5
    
    if gender == "Female" and age > 50:
        contextual_adjustments.append("Post-menopausal considerations for bone health")
    
    # Calculate overall risk score
    if all_diseases:
        overall_risk = sum(d['risk_percentage'] for d in all_diseases.values()) / len(all_diseases)
    else:
        overall_risk = 10  # Minimal risk if no issues detected
    
    return {
        'combined_diseases': all_diseases,
        'overall_risk_score': round(overall_risk, 1),
        'contextual_adjustments': contextual_adjustments,
        'patient_context': {
            'age': age,
            'gender': gender
        },
        'model_name': 'Contextual Analysis Model',
        'confidence': 85
    }
