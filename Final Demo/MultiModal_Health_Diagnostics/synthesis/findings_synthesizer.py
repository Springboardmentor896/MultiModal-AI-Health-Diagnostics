"""
Findings Synthesizer
Combines results from all models into unified analysis
"""

from typing import Dict, Any


class HealthSynthesizer:
    """
    Synthesizes findings from multiple models
    """
    
    def __init__(self):
        self.name = "Health_Synthesizer"
    
    def synthesize(self, lab_data, patient_info, model1_output, model2_output, model3_output, query):
        """
        Main synthesis method
        
        Args:
            lab_data: Extracted lab parameters
            patient_info: Patient demographics
            model1_output: Clinical rules output
            model2_output: ML risk output
            model3_output: Contextual analysis output
            query: User query
        
        Returns:
            dict: Synthesized analysis
        """
        # Use Model 3 risks (already synthesized from Model 1 & 2)
        risks = model3_output.get('risks', {})
        
        # Generate synthesis summary
        summary = self._create_summary(lab_data, risks, patient_info)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risks, lab_data, patient_info)
        
        return {
            'patient': patient_info,
            'lab_data': lab_data,
            'risks': risks,
            'synthesis_summary': summary,
            'recommendations': recommendations,
            'model_outputs': {
                'model1': model1_output,
                'model2': model2_output,
                'model3': model3_output
            }
        }
    
    def _create_summary(self, lab_data, risks, patient_info):
        """Create synthesis summary"""
        findings = []
        abnormal_params = []
        
        # Check each lab parameter against normal ranges
        gender = patient_info.get('gender', 'male')
        
        # Define reference ranges
        if gender == 'male':
            ref_ranges = {
                'hemoglobin': (13.0, 17.0),
                'rbc': (4.5, 5.5),
                'wbc': (4000, 11000),
                'platelets': (150000, 410000)
            }
        else:
            ref_ranges = {
                'hemoglobin': (12.0, 16.0),
                'rbc': (4.0, 5.0),
                'wbc': (4000, 11000),
                'platelets': (150000, 410000)
            }
        
        # Check for abnormal values
        for param, value in lab_data.items():
            if param in ref_ranges:
                min_val, max_val = ref_ranges[param]
                param_name = param.replace('_', ' ').title()
                
                if value < min_val:
                    status = 'low'
                    abnormal_params.append(param)
                    findings.append(f"{param_name} is {status} ({value} vs {min_val}-{max_val})")
                elif value > max_val:
                    status = 'high'
                    abnormal_params.append(param)
                    findings.append(f"{param_name} is {status} ({value} vs {min_val}-{max_val})")
        
        # Add high/moderate risk findings
        high_risks = []
        moderate_risks = []
        
        for disease, risk_data in risks.items():
            disease_name = disease.replace('_', ' ').title()
            prob = risk_data['probability'] * 100
            label = risk_data['label']
            
            if label == 'high':
                high_risks.append(disease)
                findings.append(f"{disease_name}: {prob:.1f}% probability (HIGH risk)")
            elif label == 'moderate':
                moderate_risks.append(disease)
                findings.append(f"{disease_name}: {prob:.1f}% probability (MODERATE risk)")
        
        # Determine overall risk
        if high_risks:
            overall_risk = "high"
        elif moderate_risks:
            overall_risk = "moderate"
        else:
            overall_risk = "low"
        
        # Calculate average risk score
        if risks:
            risk_score = sum(r['probability'] for r in risks.values()) / len(risks)
        else:
            risk_score = 0.05
        
        return {
            "key_findings": findings if findings else ["No significant abnormal findings detected"],
            "abnormal_parameters": abnormal_params,
            "high_risks": high_risks,
            "moderate_risks": moderate_risks,
            "overall_risk": overall_risk,
            "risk_score": round(risk_score, 3),
            "risk_probability": round(risk_score * 100, 1)
        }
    
    def _generate_recommendations(self, risks, lab_data, patient_info):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Sort risks by probability
        sorted_risks = sorted(risks.items(), key=lambda x: x[1]['probability'], reverse=True)
        
        # Generate recommendations for top risks
        for disease, risk_data in sorted_risks[:5]:  # Top 5 risks
            if risk_data['label'] in ['high', 'moderate']:
                rec = self._get_disease_recommendation(disease, risk_data, lab_data, patient_info)
                recommendations.append(rec)
        
        return recommendations
    
    def _get_disease_recommendation(self, disease, risk_data, lab_data, patient_info):
        """Get specific recommendations for each disease"""
        disease_name = disease.replace('_', ' ').title()
        priority = risk_data['label']
        
        # Disease-specific recommendations
        recommendations_map = {
            'anemia': {
                'tests': ['Complete Iron Panel', 'Vitamin B12', 'Folate levels', 'Reticulocyte count'],
                'lifestyle': ['Iron-rich diet (spinach, red meat, lentils)', 'Vitamin C for iron absorption', 'Avoid tea/coffee with meals'],
                'referral': 'Hematologist consultation recommended'
            },
            'infection': {
                'tests': ['Blood culture', 'CRP', 'Procalcitonin', 'Chest X-ray if respiratory symptoms'],
                'lifestyle': ['Rest and hydration', 'Monitor fever', 'Complete antibiotic course if prescribed'],
                'referral': 'Infectious disease specialist if persistent'
            },
            'cardiovascular': {
                'tests': ['Lipid profile', 'ECG', 'Echocardiogram', 'Blood pressure monitoring'],
                'lifestyle': ['Low-salt diet', 'Regular exercise (30 min/day)', 'Stress management', 'Quit smoking'],
                'referral': 'Cardiologist evaluation recommended'
            },
            'diabetes': {
                'tests': ['Fasting glucose', 'HbA1c', 'Glucose tolerance test', 'Lipid profile'],
                'lifestyle': ['Low glycemic index diet', 'Regular exercise', 'Weight management', 'Monitor blood sugar'],
                'referral': 'Endocrinologist consultation'
            },
            'kidney_dysfunction': {
                'tests': ['Serum creatinine', 'BUN', 'Urinalysis', 'Kidney ultrasound'],
                'lifestyle': ['Adequate hydration', 'Low-protein diet', 'Control blood pressure', 'Limit salt'],
                'referral': 'Nephrologist consultation recommended'
            },
            'liver_dysfunction': {
                'tests': ['Liver function tests (ALT, AST, ALP)', 'Bilirubin', 'Hepatitis panel', 'Liver ultrasound'],
                'lifestyle': ['Avoid alcohol', 'Healthy diet', 'Limit processed foods', 'Maintain healthy weight'],
                'referral': 'Hepatologist consultation'
            },
            'thyroid_dysfunction': {
                'tests': ['TSH', 'Free T3', 'Free T4', 'Thyroid antibodies'],
                'lifestyle': ['Regular monitoring', 'Iodine-rich diet', 'Stress management'],
                'referral': 'Endocrinologist evaluation'
            },
            'hypertension': {
                'tests': ['Blood pressure monitoring', 'ECG', 'Kidney function tests', 'Lipid profile'],
                'lifestyle': ['DASH diet', 'Reduce sodium intake', 'Regular exercise', 'Weight loss if overweight'],
                'referral': 'Cardiologist if BP >140/90 consistently'
            }
        }
        
        # Get recommendation or use default
        rec_data = recommendations_map.get(disease, {
            'tests': ['Consult healthcare provider for appropriate tests'],
            'lifestyle': ['Maintain healthy lifestyle', 'Regular monitoring'],
            'referral': 'Healthcare provider consultation recommended'
        })
        
        return {
            'disease': disease_name,
            'priority': priority,
            'tests': rec_data['tests'],
            'lifestyle': rec_data['lifestyle'],
            'referral': rec_data['referral'] if priority == 'high' else None
        }


# Legacy function for backward compatibility
def synthesize_findings(interpreted: Dict[str, Any], risks: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function - kept for backward compatibility
    """
    synthesizer = HealthSynthesizer()
    # This would need proper conversion - use the class instead
    return {
        "key_findings": [],
        "abnormal_parameters": [],
        "overall_risk": "low",
        "risk_score": 0.05
    }
