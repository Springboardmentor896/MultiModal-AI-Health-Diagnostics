"""
Model-2: Pattern Recognition Engine
Identifies medical patterns and calculates risk scores from blood parameters
"""

import json
import pandas as pd
from typing import Dict, List, Tuple, Any
import numpy as np

class PatternEngine:
    def __init__(self, patterns_file: str = "medical_patterns.json"):
        """Initialize pattern engine with medical patterns."""
        with open(patterns_file, 'r') as f:
            self.patterns = json.load(f)['patterns']
    
    def evaluate_trigger(self, param: str, value: float, trigger: str) -> bool:
        """Evaluate if a parameter value triggers a condition."""
        if trigger.startswith('>'):
            threshold = float(trigger[1:])
            return value > threshold
        elif trigger.startswith('<'):
            threshold = float(trigger[1:])
            return value < threshold
        return False
    
    def detect_patterns(self, blood_values: Dict[str, float]) -> List[Dict]:
        """Detect all triggered medical patterns."""
        detected = []
        
        for pattern in self.patterns:
            triggers_met = 0
            total_triggers = len(pattern['triggers'])
            
            for trigger in pattern['triggers']:
                for param, condition in trigger.items():
                    if param in blood_values:
                        if self.evaluate_trigger(param, blood_values[param], condition):
                            triggers_met += 1
            
            if triggers_met > 0:
                confidence = (triggers_met / total_triggers) * pattern['confidence']
                detected.append({
                    'pattern_id': pattern['id'],
                    'name': pattern['name'],
                    'risk_level': pattern['risk_level'],
                    'confidence': min(100, confidence),
                    'recommendations': pattern['recommendations']
                })
        
        return detected
    
    def calculate_risk_score(self, detected_patterns: List[Dict]) -> float:
        """Calculate total risk score from detected patterns."""
        risk_mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        total_risk = sum(risk_mapping.get(p['risk_level'], 1) * (p['confidence']/100) 
                        for p in detected_patterns)
        return round(total_risk, 2)
    
    def get_risk_category(self, risk_score: float) -> str:
        """Convert risk score to category."""
        if risk_score == 0:
            return "NORMAL"
        elif risk_score < 2:
            return "LOW"
        elif risk_score < 3:
            return "MEDIUM"
        elif risk_score < 4:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def generate_report(self, blood_values: Dict[str, float]) -> Dict:
        """Generate complete pattern analysis report."""
        patterns = self.detect_patterns(blood_values)
        risk_score = self.calculate_risk_score(patterns)
        risk_category = self.get_risk_category(risk_score)
        
        return {
            'detected_patterns': patterns,
            'risk_score': risk_score,
            'risk_category': risk_category,
            'total_patterns': len(patterns),
            'is_critical': risk_score >= 4.0
        }

# Test the engine
if __name__ == "__main__":
    engine = PatternEngine()
    
    # Example from your whiteboard
    test_patient = {
        'hemoglobin': 11.0,
        'white_blood_cells': 14000,
        'platelet_count': 140000,
        'glucose': 150,
        'cholesterol': 260
    }
    
    report = engine.generate_report(test_patient)
    print("=== Model-2 Pattern Analysis ===")
    print(json.dumps(report, indent=2))