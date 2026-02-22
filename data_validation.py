#!/usr/bin/env python3
"""
data_validation.py
Data cleaning, validation, and quality assurance
Part of: Health Diagnostics Project - Week 1-2 Data Preparation
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List

class BloodDataValidator:
    """Validate and clean blood count data"""
    
    def __init__(self):
        self.critical_ranges = {
            'hemoglobin': (7.0, 20.0),
            'platelet_count': (50000, 1000000),
            'white_blood_cells': (2000, 30000),
            'red_blood_cells': (2.0, 8.0),
            'mcv': (50, 150),
            'mch': (15, 50),
            'mchc': (25, 40)
        }
    
    def check_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """Check for missing values in dataset"""
        return df.isnull().sum().to_dict()
    
    def check_outliers(self, df: pd.DataFrame) -> Dict[str, List[int]]:
        """
        Identify outliers based on critical ranges
        Returns row indices of records with outliers
        """
        outliers = {}
        column_mapping = {
            'Hemoglobin': 'hemoglobin',
            'Platelet_Count': 'platelet_count',
            'White_Blood_Cells': 'white_blood_cells',
            'Red_Blood_Cells': 'red_blood_cells',
            'MCV': 'mcv',
            'MCH': 'mch',
            'MCHC': 'mchc'
        }
        
        for col, param_key in column_mapping.items():
            if col in df.columns and param_key in self.critical_ranges:
                min_val, max_val = self.critical_ranges[param_key]
                outlier_mask = (df[col] < min_val) | (df[col] > max_val)
                outliers[col] = df[outlier_mask].index.tolist()
        
        return outliers
    
    def check_consistency(self, df: pd.DataFrame) -> Dict[str, List]:
        """
        Check for internal data consistency
        E.g., MCV should correlate with RBC and Hemoglobin
        """
        issues = []
        
        # RBC count and Hemoglobin correlation check
        if 'Red_Blood_Cells' in df.columns and 'Hemoglobin' in df.columns:
            # Low RBC should usually mean low Hemoglobin
            inconsistent = df[(df['Red_Blood_Cells'] < 4.5) & (df['Hemoglobin'] > 15)].index.tolist()
            if inconsistent:
                issues.append({
                    'type': 'consistency_warning',
                    'message': 'Low RBC with high Hemoglobin detected',
                    'rows': inconsistent
                })
        
        return {'consistency_issues': issues}
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict:
        """
        Complete validation report
        """
        report = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'missing_values': self.check_missing_values(df),
            'outliers': self.check_outliers(df),
            'consistency_checks': self.check_consistency(df)
        }
        
        return report
    
    def clean_dataframe(self, df: pd.DataFrame, remove_outliers: bool = False) -> pd.DataFrame:
        """
        Clean dataframe by handling outliers
        """
        df_clean = df.copy()
        
        if remove_outliers:
            outliers = self.check_outliers(df)
            rows_to_remove = set()
            for col, row_indices in outliers.items():
                rows_to_remove.update(row_indices)
            
            df_clean = df_clean.drop(list(rows_to_remove))
            print(f"Removed {len(rows_to_remove)} records with outliers")
        
        return df_clean
    
    def generate_validation_report(self, df: pd.DataFrame) -> str:
        """Generate detailed validation report"""
        report = self.validate_dataframe(df)
        
        output = "=" * 70 + "\n"

        output += "DATA VALIDATION REPORT\n"
        output += "="*70 + "\n\n"
        
        output += f"📊 Dataset Overview:\n"
        output += f"  Total Records: {report['total_records']}\n"
        output += f"  Total Columns: {report['total_columns']}\n\n"
        
        output += f"❌ Missing Values:\n"
        for col, count in report['missing_values'].items():
            if count > 0:
                output += f"  {col}: {count}\n"
        
        output += f"\n⚠️  Outliers Detected:\n"
        outlier_count = sum(len(rows) for rows in report['outliers'].values())
        if outlier_count == 0:
            output += "  None detected ✅\n"
        else:
            for col, rows in report['outliers'].items():
                if rows:
                    output += f"  {col}: {len(rows)} outliers\n"
        
        output += f"\n✅ Validation Complete\n"
        
        return output


def generate_data_quality_summary(csv_path: str) -> None:
    """Generate and print data quality summary"""
    df = pd.read_csv(csv_path)
    validator = BloodDataValidator()
    
    print(validator.generate_validation_report(df))
    
    # Additional statistics
    print("\n" + "="*70)
    print("STATISTICAL SUMMARY")
    print("="*70 + "\n")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        print(f"{col}:")
        print(f"  Mean: {df[col].mean():.2f}")
        print(f"  Median: {df[col].median():.2f}")
        print(f"  Std Dev: {df[col].std():.2f}")
        print(f"  Min: {df[col].min():.2f}")
        print(f"  Max: {df[col].max():.2f}")
        print()


# Example Usage
if __name__ == "__main__":
    csv_path = "blood_count_dataset.csv"
    generate_data_quality_summary(csv_path)
