"""
Model 2: Statistical/ML-Based Risk Assessment
"""

import math


class Model2MLRisk:
    def __init__(self):
        self.name = "Statistical_ML_Model"
        
        self.disease_weights = {
            'anemia': {
                'hemoglobin': -0.8,
                'rbc': -0.6,
                'mcv': 0.3,
                'mch': 0.2
            },
            'infection': {
                'wbc': 0.7,
                'neutrophils': 0.6,
                'lymphocytes': 0.4
            },
            'cardiovascular': {
                'platelets': 0.3,
                'rbc': 0.2,
                'age': 0.5
            },
            'diabetes': {
                'age': 0.4,
                'wbc': 0.2
            },
            'kidney_dysfunction': {
                'hemoglobin': -0.5,
                'rbc': -0.4,
                'wbc': 0.3
            },
            'liver_dysfunction': {
                'platelets': -0.6,
                'wbc': 0.3
            },
            'thyroid_dysfunction': {
                'wbc': 0.1
            },
            'hypertension': {
                'rbc': 0.4,
                'age': 0.5
            }
        }
        
        # Reference ranges for direct comparison
        self.ref_ranges = {
            'male': {
                'hemoglobin': (13.0, 17.0),
                'rbc': (4.5, 5.5),
                'wbc': (4000, 11000),
                'platelets': (150000, 410000),
                'neutrophils': (40, 70),
                'lymphocytes': (20, 40),
                'mcv': (83, 101),
                'mch': (27, 32)
            },
            'female': {
                'hemoglobin': (12.0, 16.0),
                'rbc': (4.0, 5.0),
                'wbc': (4000, 11000),
                'platelets': (150000, 410000),
                'neutrophils': (40, 70),
                'lymphocytes': (20, 40),
                'mcv': (83, 101),
                'mch': (27, 32)
            }
        }
    
    def analyze(self, lab_data, patient_info):
        """Main analysis"""
        gender = patient_info.get('gender', 'male').lower()
        age = patient_info.get('age', 30)
        ranges = self.ref_ranges.get(gender, self.ref_ranges['male'])
        
        # Calculate deviations from normal range
        deviations = self._calculate_deviations(lab_data, ranges, age)
        
        # Calculate risk for each disease
        risks = {}
        for disease, weights in self.disease_weights.items():
            risk_prob = self._calculate_disease_risk(deviations, weights, disease)
            risks[disease] = {
                'probability': risk_prob,
                'label': self._risk_label(risk_prob * 100),
                'confidence': self._calculate_confidence(lab_data, weights),
                'feature_importance': self._get_feature_importance(weights)
            }
        
        return {
            'model': self.name,
            'risks': risks,
            'metadata': {'deviations': deviations}
        }
    
    def _calculate_deviations(self, lab_data, ranges, age):
        """
        Calculate deviation score for each parameter.
        0 = normal, positive = above normal, negative = below normal
        Scale: 1.0 = 100% outside the range
        """
        deviations = {}
        
        for param, (low, high) in ranges.items():
            if param not in lab_data:
                deviations[param] = 0.0  # No data = assume normal
                continue
            
            value = lab_data[param]
            range_size = high - low
            
            if value < low:
                # Below normal - negative deviation
                deviations[param] = -((low - value) / range_size)
            elif value > high:
                # Above normal - positive deviation
                deviations[param] = (value - high) / range_size
            else:
                # Within normal range
                deviations[param] = 0.0
        
        # Age deviation (higher age = higher risk for age-related diseases)
        deviations['age'] = max(0, (age - 40) / 60)  # 0 below 40, increases after
        
        return deviations
    
    def _calculate_disease_risk(self, deviations, weights, disease):
        """Calculate disease probability from deviations"""
        
        # Count available features
        available = sum(1 for f in weights.keys() if f in deviations and deviations[f] != 0.0)
        total = len(weights)
        
        score = 0.0
        for feature, weight in weights.items():
            if feature not in deviations:
                continue
            
            deviation = deviations[feature]
            
            if deviation == 0.0:
                # Normal - no contribution to risk
                continue
            
            if weight < 0:
                # Negative weight = low values are bad
                if deviation < 0:
                    score += abs(weight) * abs(deviation)
            else:
                # Positive weight = high values are bad
                if deviation > 0:
                    score += weight * deviation
        
        # No abnormal findings - return baseline
        if score == 0:
            return 0.05
        
        # Convert score to probability
        # score=0.5 → ~50%, score=0.25 → ~25%, score=0.1 → ~10%
        probability = min(0.95, max(0.05, score * 0.8 + 0.05))
        
        return round(probability, 3)
    
    def _normalize_features(self, lab_data, patient_info):
        """Kept for compatibility - returns deviations"""
        gender = patient_info.get('gender', 'male').lower()
        age = patient_info.get('age', 30)
        ranges = self.ref_ranges.get(gender, self.ref_ranges['male'])
        return self._calculate_deviations(lab_data, ranges, age)
    
    def _calculate_confidence(self, lab_data, weights):
        """Confidence based on available features"""
        total = len(weights)
        available = sum(1 for f in weights.keys() if f in lab_data)
        return round((available / total) * 100, 1)
    
    def _get_feature_importance(self, weights):
        """Sorted feature importance"""
        return {f: abs(w) for f, w in sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)}
    
    def _risk_label(self, score):
        """Convert score to label"""
        if score >= 50:
            return 'high'
        elif score >= 20:
            return 'moderate'
        else:
            return 'low'
