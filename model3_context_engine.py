"""
Model-3: Context Engine (Age & Gender Adjustments)
Adjusts interpretations based on demographic context
"""

import json
import pandas as pd
from typing import Dict, Tuple, Any
from model2_pattern_engine import PatternEngine

class ContextEngine:
    def __init__(self, adjustments_file: str = "age_gender_adjustments.json"):
        """Initialize context engine with age-gender adjustments."""
        with open(adjustments_file, 'r') as f:
            self.adjustments = json.load(f)
    
    def get_age_group(self, age: int) -> str:
        """Classify age into group."""
        if age <= 35:
            return "young"
        elif age <= 50:
            return "middle"
        elif age <= 65:
            return "senior"
        else:
            return "elderly"
    
    def get_adjusted_thresholds(self, age: int, gender: str, param: str) -> Tuple[float, float]:
        """Get age-gender adjusted reference ranges."""
        age_group = self.get_age_group(age)
        try:
            low = self.adjustments['parameter_adjustments'][param][gender][age_group][0]
            high = self.adjustments['parameter_adjustments'][param][gender][age_group][1]
            return low, high
        except (KeyError, IndexError):
            # Fallback to standard ranges
            standard = {'hemoglobin': (12.0, 16.0), 'glucose': (70, 100), 'cholesterol': (0, 200)}
            return standard.get(param, (0, 100))
    
    def classify_with_context(self, param: str, value: float, age: int, 
                            gender: str) -> Dict[str, Any]:
        """Classify parameter value with age-gender context."""
        low, high = self.get_adjusted_thresholds(age, gender, param)
        status = "Low" if value < low else "High" if value > high else "Normal"
        
        context_notes = {
            "age_group": self.get_age_group(age),
            "adjusted_range": [low, high],
            "original_status": status,
            "context_note": f"Age {age} {gender} range: {low}-{high}"
        }
        
        return {
            'parameter': param,
            'value': value,
            'status': status,
            'context': context_notes
        }
    
    def adjust_pattern_interpretation(self, patterns: list, age: int, gender: str) -> list:
        """Adjust pattern risk based on age-gender context."""
        adjusted = []
        age_group = self.get_age_group(age)
        age_multiplier = self.adjustments['age_groups'][age_group]['multiplier']
        
        for pattern in patterns:
            # Seniors/elderly have slightly lower risk perception for certain patterns
            adjusted_risk = pattern['risk_level']
            if age_group in ['senior', 'elderly'] and adjusted_risk == 'HIGH':
                adjusted_risk = 'MEDIUM'
            
            adjusted.append({
                **pattern,
                'age_adjusted_risk': adjusted_risk,
                'age_multiplier': age_multiplier,
                'age_group': age_group
            })
        
        return adjusted

# Test the context engine  
if __name__ == "__main__":
    context = ContextEngine()
    
    # Test patient from whiteboard (Age 68, Female)
    classifications = context.classify_with_context('hemoglobin', 11.0, 68, 'female')
    print("=== Model-3 Context Analysis ===")
    print(json.dumps(classifications, indent=2, default=str))