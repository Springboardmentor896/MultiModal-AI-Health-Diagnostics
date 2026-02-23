"""
Model 1: Rule-Based Clinical Logic
Implements evidence-based medical guidelines for risk assessment
"""

class Model1Interpreter:
    def __init__(self):
        self.name = "Clinical_Rules_Model"
        
        # Reference ranges by gender
        self.reference_ranges = {
            'male': {
                'hemoglobin': (13.0, 17.0),
                'rbc': (4.5, 5.5),
                'wbc': (4000, 11000),
                'platelets': (150000, 410000),
                'neutrophils': (40, 70),
                'lymphocytes': (20, 40),
                'mcv': (83, 101),
                'mch': (27, 32),
                'mchc': (32.5, 34.5)
            },
            'female': {
                'hemoglobin': (12.0, 16.0),
                'rbc': (4.0, 5.0),
                'wbc': (4000, 11000),
                'platelets': (150000, 410000),
                'neutrophils': (40, 70),
                'lymphocytes': (20, 40),
                'mcv': (83, 101),
                'mch': (27, 32),
                'mchc': (32.5, 34.5)
            }
        }
    
    def analyze(self, lab_data, patient_info):
        """Main analysis method"""
        gender = patient_info.get('gender', 'male').lower()
        age = patient_info.get('age', 30)
        pregnant = patient_info.get('pregnant', False)
        
        # Get reference ranges for this patient
        ranges = self.reference_ranges.get(gender, self.reference_ranges['male'])
        
        # Calculate risks for each disease
        risks = {
            'anemia': self._assess_anemia(lab_data, ranges, gender, pregnant),
            'infection': self._assess_infection(lab_data, ranges),
            'cardiovascular': self._assess_cardiovascular(lab_data, age),
            'diabetes': self._assess_diabetes(lab_data, age),
            'kidney_dysfunction': self._assess_kidney(lab_data),
            'liver_dysfunction': self._assess_liver(lab_data),
            'thyroid_dysfunction': self._assess_thyroid(lab_data),
            'hypertension': self._assess_hypertension(lab_data, age)
        }
        
        return {
            'model': self.name,
            'risks': risks,
            'metadata': {
                'reference_ranges': ranges,
                'patient_gender': gender,
                'patient_age': age
            }
        }
    
    def _assess_anemia(self, data, ranges, gender, pregnant):
        """Assess anemia risk based on hemoglobin and RBC"""
        # Get actual values - NO DEFAULTS
        hb = data.get('hemoglobin')
        rbc = data.get('rbc')
        mcv = data.get('mcv', 90)
        
        # If no data, return baseline only
        if hb is None:
            return {
                'probability': 0.05,
                'label': 'low',
                'evidence': ['Hemoglobin data not available'],
                'contributing_factors': []
            }
        
        hb_min, hb_max = ranges['hemoglobin']
        rbc_min, rbc_max = ranges['rbc']
        
        evidence = []
        risk_score = 0
        
        # Hemoglobin analysis
        if hb < hb_min:
            deviation = ((hb_min - hb) / hb_min) * 100
            risk_score += min(deviation * 2, 60)
            evidence.append(f"Hemoglobin {hb} g/dL is below normal range ({hb_min}-{hb_max})")
        elif hb < hb_min + 0.5:
            risk_score += 10
            evidence.append(f"Hemoglobin {hb} g/dL is borderline low")
        
        # RBC count analysis
        if rbc and rbc < rbc_min:
            deviation = ((rbc_min - rbc) / rbc_min) * 100
            risk_score += min(deviation * 1.5, 30)
            evidence.append(f"RBC count {rbc} is below normal range ({rbc_min}-{rbc_max})")
        
        # MCV analysis for anemia type
        if risk_score > 0:
            if mcv < 80:
                evidence.append("Low MCV suggests microcytic anemia (possible iron deficiency)")
                risk_score += 10
            elif mcv > 100:
                evidence.append("High MCV suggests macrocytic anemia (possible B12/folate deficiency)")
                risk_score += 10
        
        # Cap at 95%
        risk_score = min(risk_score, 95)
        
        # If no evidence, baseline risk
        if not evidence:
            risk_score = 5
            evidence.append("Hemoglobin within normal range")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['hemoglobin', 'rbc', 'mcv']
        }
    
    def _assess_infection(self, data, ranges):
        """Assess infection risk based on WBC and differential count"""
        wbc = data.get('wbc')
        neutrophils = data.get('neutrophils')
        lymphocytes = data.get('lymphocytes')
        
        # If no WBC data, return baseline
        if wbc is None:
            return {
                'probability': 0.05,
                'label': 'low',
                'evidence': ['WBC data not available'],
                'contributing_factors': []
            }
        
        wbc_min, wbc_max = ranges['wbc']
        neut_min, neut_max = ranges['neutrophils']
        
        evidence = []
        risk_score = 0
        
        # WBC analysis
        if wbc > wbc_max:
            deviation = ((wbc - wbc_max) / wbc_max) * 100
            risk_score += min(deviation * 3, 50)
            evidence.append(f"Elevated WBC count {wbc} (normal: {wbc_min}-{wbc_max})")
        elif wbc < wbc_min:
            risk_score += 20
            evidence.append(f"Low WBC count {wbc} suggests immunosuppression")
        
        # Neutrophil analysis
        if neutrophils:
            if neutrophils > neut_max:
                risk_score += 25
                evidence.append(f"Elevated neutrophils {neutrophils}% suggests bacterial infection")
            elif neutrophils < neut_min:
                risk_score += 15
                evidence.append(f"Low neutrophils {neutrophils}% suggests viral infection")
        
        # Lymphocyte analysis
        if lymphocytes and lymphocytes > 45:
            risk_score += 20
            evidence.append(f"Elevated lymphocytes {lymphocytes}% suggests viral/chronic infection")
        
        risk_score = min(risk_score, 95)
        
        if not evidence:
            risk_score = 5
            evidence.append("WBC parameters within normal range")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['wbc', 'neutrophils', 'lymphocytes']
        }
    
    def _assess_cardiovascular(self, data, age):
        """Assess cardiovascular risk"""
        platelets = data.get('platelets')
        rbc = data.get('rbc')
        hb = data.get('hemoglobin')
        
        evidence = []
        risk_score = 0
        
        # Age factor
        if age > 50:
            risk_score += 15
            evidence.append(f"Age {age} increases cardiovascular risk")
        elif age > 40:
            risk_score += 10
        
        # Platelet abnormalities
        if platelets:
            if platelets > 450000:
                risk_score += 20
                evidence.append(f"Elevated platelets {platelets} may increase clot risk")
            elif platelets < 100000:
                risk_score += 15
                evidence.append(f"Low platelets {platelets} may indicate bleeding risk")
        
        # Anemia contribution
        if hb and hb < 12.0:
            risk_score += 10
            evidence.append("Anemia can strain cardiovascular system")
        
        risk_score = min(risk_score, 95)
        
        if not evidence:
            risk_score = 5
            evidence.append("No significant cardiovascular risk factors detected")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['age', 'platelets', 'hemoglobin']
        }
    
    def _assess_diabetes(self, data, age):
        """Assess diabetes risk - limited without glucose data"""
        wbc = data.get('wbc')
        
        evidence = []
        risk_score = 0
        
        # Age factor
        if age > 45:
            risk_score += 10
            evidence.append(f"Age {age} increases diabetes risk")
        
        # Elevated WBC can indicate inflammation
        if wbc and wbc > 10000:
            risk_score += 5
            evidence.append("Mild inflammation may be associated with metabolic syndrome")
        
        risk_score = min(risk_score, 95)
        
        if not evidence:
            risk_score = 5
            evidence.append("Limited data - glucose testing needed for accurate assessment")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['age', 'wbc']
        }
    
    def _assess_kidney(self, data):
        """Assess kidney dysfunction risk"""
        rbc = data.get('rbc')
        hb = data.get('hemoglobin')
        wbc = data.get('wbc')
        
        evidence = []
        risk_score = 0
        
        # Anemia is common in kidney disease
        if hb:
            if hb < 11.0:
                risk_score += 20
                evidence.append(f"Severe anemia (Hb {hb}) may indicate chronic kidney disease")
            elif hb < 12.0:
                risk_score += 10
                evidence.append("Mild anemia can be associated with kidney dysfunction")
        
        # Elevated WBC
        if wbc and wbc > 12000:
            risk_score += 10
            evidence.append("Elevated WBC may indicate kidney inflammation")
        
        risk_score = min(risk_score, 95)
        
        if not evidence:
            risk_score = 5
            evidence.append("No indicators - creatinine/BUN testing recommended")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['hemoglobin', 'wbc']
        }
    
    def _assess_liver(self, data):
        """Assess liver dysfunction risk"""
        platelets = data.get('platelets')
        wbc = data.get('wbc')
        
        evidence = []
        risk_score = 0
        
        # Low platelets can indicate liver disease
        if platelets:
            if platelets < 100000:
                risk_score += 25
                evidence.append(f"Low platelets {platelets} may indicate liver dysfunction")
            elif platelets < 150000:
                risk_score += 10
                evidence.append("Borderline platelets warrant monitoring")
        
        # Elevated WBC
        if wbc and wbc > 11000:
            risk_score += 10
            evidence.append("Elevated WBC may indicate liver inflammation")
        
        risk_score = min(risk_score, 95)
        
        if not evidence:
            risk_score = 5
            evidence.append("No indicators - liver function tests recommended")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['platelets', 'wbc']
        }
    
    def _assess_thyroid(self, data):
        """Assess thyroid dysfunction risk"""
        evidence = []
        risk_score = 5  # Baseline only
        
        evidence.append("Thyroid function tests (TSH, T3, T4) needed for assessment")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': []
        }
    
    def _assess_hypertension(self, data, age):
        """Assess hypertension risk"""
        rbc = data.get('rbc')
        hb = data.get('hemoglobin')
        
        evidence = []
        risk_score = 0
        
        # Age factor
        if age > 50:
            risk_score += 15
            evidence.append(f"Age {age} increases hypertension risk")
        elif age > 40:
            risk_score += 10
        
        # Polycythemia can indicate secondary hypertension
        if (rbc and rbc > 6.0) or (hb and hb > 18.0):
            risk_score += 20
            evidence.append("Elevated RBC/Hb may be secondary to hypertension")
        
        risk_score = min(risk_score, 95)
        
        if not evidence:
            risk_score = 5
            evidence.append("Blood pressure measurement needed for assessment")
        
        return {
            'probability': risk_score / 100,
            'label': self._risk_label(risk_score),
            'evidence': evidence,
            'contributing_factors': ['age', 'rbc', 'hemoglobin']
        }
    
    def _risk_label(self, score):
        """Convert numeric score to categorical label"""
        if score >= 50:
            return 'high'
        elif score >= 20:
            return 'moderate'
        else:
            return 'low'
