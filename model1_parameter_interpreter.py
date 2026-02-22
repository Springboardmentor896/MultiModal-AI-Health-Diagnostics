#!/usr/bin/env python3
"""
model1_parameter_interpreter.py
Model 1: Classify blood parameters as Low/Normal/High
Part of: Health Diagnostics Project - Week 3-4 Pattern Recognition
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List

class ParameterInterpreter:
    """
    Model 1: Parameter Interpretation
    Classifies individual blood parameters based on reference ranges
    """
    
    def __init__(self, parameter_ranges_path="parameter_ranges.json"):
        """Load parameter reference ranges"""
        with open(parameter_ranges_path, 'r') as f:
            self.ranges = json.load(f)
    
    def classify_single_parameter(self, param_name: str, value: float) -> str:
        """Classify a single parameter as Low/Normal/High"""
        if param_name not in self.ranges or value is None:
            return "Unknown"
        
        ranges = self.ranges[param_name]
        low = ranges['low']
        high = ranges['high']
        
        if value < low:
            return "Low"
        elif value > high:
            return "High"
        else:
            return "Normal"
    
    def classify_parameters(self, params: Dict[str, float]) -> Dict[str, str]:
        """
        Classify all parameters in a patient record
        Input: {'hemoglobin': 11.2, 'glucose': 130, ...}
        Output: {'hemoglobin': 'Low', 'glucose': 'High', ...}
        """
        classifications = {}
        for param, value in params.items():
            classifications[param] = self.classify_single_parameter(param, value)
        return classifications
    
    def get_risk_score(self, classifications: Dict[str, str]) -> float:
        """
        Calculate overall risk score based on abnormal parameters
        Low abnormality = 0.5, High abnormality = 1.0
        Score range: 0.0 (all normal) to 1.0 (critical)
        """
        abnormal_count = sum(1 for status in classifications.values() if status != "Normal")
        total_count = len(classifications)
        
        if total_count == 0:
            return 0.0
        
        risk_score = abnormal_count / total_count
        return min(risk_score, 1.0)
    
    def generate_health_status(self, classifications: Dict[str, str]) -> str:
        """Generate overall health status"""
        risk = self.get_risk_score(classifications)
        
        if risk == 0.0:
            return "🟢 NORMAL - All parameters are within normal range"
        elif risk < 0.3:
            return "🟡 CAUTION - Some mild abnormalities detected"
        elif risk < 0.6:
            return "🟠 WARNING - Multiple abnormal parameters detected"
        else:
            return "🔴 CRITICAL - Significant abnormalities detected, medical attention needed"
    
    def interpret_results(self, params: Dict[str, float]) -> Dict:
        """
        Complete interpretation pipeline
        Returns comprehensive analysis
        """
        classifications = self.classify_parameters(params)
        risk_score = self.get_risk_score(classifications)
        health_status = self.generate_health_status(classifications)
        
        # Identify abnormal parameters
        abnormal_params = {
            param: status for param, status in classifications.items() 
            if status != "Normal"
        }
        
        return {
            "classifications": classifications,
            "risk_score": risk_score,
            "health_status": health_status,
            "abnormal_parameters": abnormal_params,
            "normal_parameters": {
                param: status for param, status in classifications.items() 
                if status == "Normal"
            }
        }


def process_csv_with_model1(csv_path: str) -> pd.DataFrame:
    """
    Process blood count CSV with Model 1
    Adds classification columns for each parameter
    """
    interpreter = ParameterInterpreter()
    
    # Load CSV
    df = pd.read_csv(csv_path)
    print(f"✅ Processing {len(df)} records...")
    
    # Parameters to classify
    param_columns = [
        'Hemoglobin', 'Platelet_Count', 'White_Blood_Cells',
        'Red_Blood_Cells', 'MCV', 'MCH', 'MCHC'
    ]
    
    # Map column names to parameter keys (lowercase with underscores)
    column_mapping = {
        'Hemoglobin': 'hemoglobin',
        'Platelet_Count': 'platelet_count',
        'White_Blood_Cells': 'white_blood_cells',
        'Red_Blood_Cells': 'red_blood_cells',
        'MCV': 'mcv',
        'MCH': 'mch',
        'MCHC': 'mchc'
    }
    
    # Add classification columns
    for col in param_columns:
        if col in df.columns:
            param_key = column_mapping[col]
            df[f'{col}_Status'] = df[col].apply(
                lambda x: interpreter.classify_single_parameter(param_key, x)
            )
    
    # Add overall risk score
    df['Risk_Score'] = df.apply(
        lambda row: interpreter.get_risk_score({
            column_mapping[col]: interpreter.classify_single_parameter(
                column_mapping[col], 
                row[col]
            )
            for col in param_columns if col in df.columns
        }),
        axis=1
    )
    
    # Add health status
    df['Health_Status'] = df['Risk_Score'].apply(
        lambda score: (
            "🟢 NORMAL" if score == 0.0 else
            "🟡 CAUTION" if score < 0.3 else
            "🟠 WARNING" if score < 0.6 else
            "🔴 CRITICAL"
        )
    )
    
    return df


# Example Usage
if __name__ == "__main__":
    interpreter = ParameterInterpreter()
    
    # Example patient data
    sample_patient = {
        'hemoglobin': 11.2,
        'platelet_count': 280000,
        'white_blood_cells': 7500,
        'red_blood_cells': 4.2,
        'mcv': 85,
        'mch': 27,
        'mchc': 32
    }
    
    print("="*60)
    print("MODEL 1: PARAMETER INTERPRETER")
    print("="*60)
    
    # Interpret
    result = interpreter.interpret_results(sample_patient)
    
    print(f"\n📊 Patient Blood Parameters:")
    for param, value in sample_patient.items():
        status = result['classifications'][param]
        print(f"  {param}: {value} → {status}")
    
    print(f"\n{result['health_status']}")
    print(f"Risk Score: {result['risk_score']:.2f} (0.0 = Normal, 1.0 = Critical)")
    
    print(f"\n⚠️  Abnormal Parameters: {result['abnormal_parameters']}")
    
    # Process CSV (uncomment to use)
    print("\n" + "="*60)
    print("Processing CSV file...")
    # df = process_csv_with_model1("blood_count_dataset.csv")
    # print(df[['Hemoglobin', 'Hemoglobin_Status', 'Risk_Score', 'Health_Status']].head(10))
    # df.to_csv("blood_count_classified.csv", index=False)
    # print(f"✅ Saved classified data to blood_count_classified.csv")
