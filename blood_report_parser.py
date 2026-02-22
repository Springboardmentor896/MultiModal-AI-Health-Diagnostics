#!/usr/bin/env python3
"""
blood_report_parser.py
Extracts blood parameters from text/PDF and validates them
Part of: Health Diagnostics Project - Week 1-2 Data Preparation
"""

import re
import json
import pandas as pd
from typing import Dict, Tuple

class BloodReportParser:
    """Parse blood count parameters from various text formats"""
    
    def __init__(self, parameter_ranges_path="parameter_ranges.json"):
        """Initialize parser with reference ranges"""
        with open(parameter_ranges_path, 'r') as f:
            self.ranges = json.load(f)
        self.parameters = {
            "hemoglobin": r"Hemoglobin\s*[:|=]?\s*([\d.]+)",
            "platelet_count": r"Platelet[\s\w]*[:|=]?\s*([\d.]+)",
            "white_blood_cells": r"White[\s\w]*Cells?[\s\w]*[:|=]?\s*([\d.]+)",
            "red_blood_cells": r"Red[\s\w]*Cells?[\s\w]*[:|=]?\s*([\d.]+)",
            "mcv": r"MCV\s*[:|=]?\s*([\d.]+)",
            "mch": r"MCH\s*[:|=]?\s*([\d.]+)",
            "mchc": r"MCHC\s*[:|=]?\s*([\d.]+)"
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("⚠️  pdfplumber not installed. Install with: pip install pdfplumber")
            return ""
    
    def extract_parameters(self, text: str) -> Dict[str, float]:
        """Extract blood parameters from raw text using regex patterns"""
        results = {}
        for param, pattern in self.parameters.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    results[param] = value
                except ValueError:
                    results[param] = None
        return results
    
    def validate_parameters(self, params: Dict[str, float]) -> Dict[str, float]:
        """
        Validate extracted parameters against ranges
        Returns cleaned parameters (None if invalid)
        """
        validated = {}
        for param, value in params.items():
            if param in self.ranges and value is not None:
                # Check if within critical thresholds
                critical_low = self.ranges[param].get('critical_low', -float('inf'))
                critical_high = self.ranges[param].get('critical_high', float('inf'))
                
                if critical_low <= value <= critical_high:
                    validated[param] = value
                else:
                    print(f"⚠️  {param}: {value} outside critical range")
                    validated[param] = None
            else:
                validated[param] = None
        return validated
    
    def classify_parameters(self, params: Dict[str, float]) -> Dict[str, str]:
        """Classify parameters as Low/Normal/High"""
        classifications = {}
        for param, value in params.items():
            if value is None or param not in self.ranges:
                classifications[param] = "Unknown"
                continue
            
            low = self.ranges[param]['low']
            high = self.ranges[param]['high']
            
            if value < low:
                classifications[param] = "Low"
            elif value > high:
                classifications[param] = "High"
            else:
                classifications[param] = "Normal"
        
        return classifications
    
    def parse_blood_report(self, text: str) -> Tuple[Dict, Dict]:
        """
        Complete pipeline: extract → validate → classify
        Returns: (validated_parameters, classifications)
        """
        # Extract raw values
        raw_params = self.extract_parameters(text)
        print(f"📊 Extracted parameters: {raw_params}")
        
        # Validate
        validated = self.validate_parameters(raw_params)
        print(f"✅ Validated parameters: {validated}")
        
        # Classify
        classified = self.classify_parameters(validated)
        print(f"📈 Classification: {classified}")
        
        return validated, classified


def parse_csv_blood_count(csv_path: str) -> pd.DataFrame:
    """
    Load blood count CSV and add classification columns
    """
    parser = BloodReportParser()
    
    # Load CSV
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} records from {csv_path}")
    
    # Add classification columns
    for param in parser.parameters.keys():
        if param in df.columns:
            df[f"{param}_status"] = df[param].apply(
                lambda x: parser.classify_parameters({param: x})[param]
            )
    
    return df


# Example Usage
if __name__ == "__main__":
    parser = BloodReportParser()
    
    # Example 1: Parse from text
    sample_text = """
    Patient Blood Report
    Hemoglobin: 11.2 g/dL
    Platelet Count: 280000 /μL
    White Blood Cells: 7500 /μL
    Red Blood Cells: 4.2 million/μL
    MCV: 85 fL
    MCH: 27 pg
    MCHC: 32 g/dL
    """
    
    params, classified = parser.parse_blood_report(sample_text)
    print(f"\n📋 Final Result:")
    for param in params.keys():
        print(f"  {param}: {params[param]} → {classified[param]}")
    
    # Example 2: Process CSV file
    print("\n" + "="*50)
    print("Processing CSV file...")
    # Uncomment to use with actual CSV:
    # df = parse_csv_blood_count("blood_count_dataset.csv")
    # print(df.head())
