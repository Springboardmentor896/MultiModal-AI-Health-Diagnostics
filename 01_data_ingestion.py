#!/usr/bin/env python3
"""
01_data_ingestion.ipynb (as Python script)
Data Loading, Exploration, and Preparation
Part of: Health Diagnostics Project - Week 1-2 Data Preparation
Run in Jupyter: jupyter notebook 01_data_ingestion.ipynb
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from blood_report_parser import BloodReportParser, parse_csv_blood_count
from model1_parameter_interpreter import ParameterInterpreter, process_csv_with_model1

# ============================================================================
# STEP 1: LOAD BLOOD COUNT DATASET
# ============================================================================
print("="*70)
print("STEP 1: LOADING BLOOD COUNT DATASET")
print("="*70)

csv_path = "blood_count_dataset.csv"
df = pd.read_csv(csv_path)

print(f"\n✅ Dataset loaded successfully!")
print(f"📊 Shape: {df.shape[0]} records × {df.shape[1]} columns")
print(f"📋 Columns: {list(df.columns)}")
print(f"\n🔍 First 5 records:")
print(df.head())

# ============================================================================
# STEP 2: EXPLORE DATA STRUCTURE
# ============================================================================
print("\n" + "="*70)
print("STEP 2: DATA EXPLORATION & STATISTICS")
print("="*70)

print("\n📊 Data Types:")
print(df.dtypes)

print("\n📈 Statistical Summary:")
print(df.describe())

print("\n❌ Missing Values:")
print(df.isnull().sum())

print("\n⚧ Gender Distribution:")
print(df['Gender'].value_counts())

print("\n👥 Age Statistics:")
print(f"  Min Age: {df['Age'].min()}")
print(f"  Max Age: {df['Age'].max()}")
print(f"  Mean Age: {df['Age'].mean():.1f}")
print(f"  Median Age: {df['Age'].median():.1f}")

# ============================================================================
# STEP 3: DATA QUALITY CHECK
# ============================================================================
print("\n" + "="*70)
print("STEP 3: DATA QUALITY VALIDATION")
print("="*70)

# Check for outliers
param_ranges = {
    'Hemoglobin': (7.0, 20.0),
    'Platelet_Count': (50000, 1000000),
    'White_Blood_Cells': (2000, 30000),
    'Red_Blood_Cells': (2.0, 8.0),
    'MCV': (50, 150),
    'MCH': (15, 50),
    'MCHC': (25, 40)
}

print("\n🔍 Checking for outliers (outside critical ranges):")
for param, (min_val, max_val) in param_ranges.items():
    if param in df.columns:
        outliers = ((df[param] < min_val) | (df[param] > max_val)).sum()
        if outliers > 0:
            print(f"  ⚠️  {param}: {outliers} outliers detected")
        else:
            print(f"  ✅ {param}: No outliers")

# ============================================================================
# STEP 4: EXTRACT AND CLASSIFY PARAMETERS
# ============================================================================
print("\n" + "="*70)
print("STEP 4: PARAMETER EXTRACTION & CLASSIFICATION")
print("="*70)

print("\n🔄 Processing all records with Model 1...")
df_classified = process_csv_with_model1(csv_path)

print("\n✅ Classification complete!")
print("\n📊 Sample classified records:")
print(df_classified[['Age', 'Gender', 'Hemoglobin', 'Hemoglobin_Status', 
                     'Risk_Score', 'Health_Status']].head(10))

# ============================================================================
# STEP 5: ANALYZE ABNORMALITIES
# ============================================================================
print("\n" + "="*70)
print("STEP 5: ABNORMALITY ANALYSIS")
print("="*70)

status_params = [col for col in df_classified.columns if col.endswith('_Status')]

print("\n📊 Abnormality Distribution:")
for param_col in status_params:
    param_name = param_col.replace('_Status', '')
    counts = df_classified[param_col].value_counts()
    print(f"\n{param_name}:")
    for status in ['Low', 'Normal', 'High']:
        count = counts.get(status, 0)
        percentage = (count / len(df_classified)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")

print("\n📈 Health Status Distribution:")
health_counts = df_classified['Health_Status'].value_counts()
for status in health_counts.index:
    count = health_counts[status]
    percentage = (count / len(df_classified)) * 100
    print(f"  {status}: {count} ({percentage:.1f}%)")

print(f"\n⚠️  Average Risk Score: {df_classified['Risk_Score'].mean():.3f}")

# ============================================================================
# STEP 6: SAVE PROCESSED DATASET
# ============================================================================
print("\n" + "="*70)
print("STEP 6: SAVING PROCESSED DATA")
print("="*70)

# Save classified data
output_csv = "blood_count_classified.csv"
df_classified.to_csv(output_csv, index=False)
print(f"✅ Saved classified data: {output_csv}")

# Save statistics
stats = {
    "total_records": len(df_classified),
    "total_parameters": len(status_params),
    "abnormal_records": (df_classified['Risk_Score'] > 0).sum(),
    "critical_records": (df_classified['Health_Status'] == "🔴 CRITICAL").sum(),
    "average_risk_score": float(df_classified['Risk_Score'].mean()),
    "gender_distribution": df_classified['Gender'].value_counts().to_dict()
}

stats_json = "data_statistics.json"
with open(stats_json, 'w') as f:
    json.dump(stats, f, indent=2)
print(f"✅ Saved statistics: {stats_json}")

# ============================================================================
# STEP 7: VISUALIZATIONS (Optional)
# ============================================================================
print("\n" + "="*70)
print("STEP 7: DATA VISUALIZATION")
print("="*70)

try:
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Hemoglobin distribution
    axes[0, 0].hist(df_classified['Hemoglobin'], bins=30, color='skyblue', edgecolor='black')
    axes[0, 0].axvline(12, color='red', linestyle='--', label='Low Threshold')
    axes[0, 0].axvline(16, color='green', linestyle='--', label='High Threshold')
    axes[0, 0].set_title('Hemoglobin Distribution')
    axes[0, 0].set_xlabel('Hemoglobin (g/dL)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    
    # Plot 2: Risk Score distribution
    axes[0, 1].hist(df_classified['Risk_Score'], bins=20, color='orange', edgecolor='black')
    axes[0, 1].set_title('Risk Score Distribution')
    axes[0, 1].set_xlabel('Risk Score')
    axes[0, 1].set_ylabel('Frequency')
    
    # Plot 3: Health Status
    health_counts = df_classified['Health_Status'].value_counts()
    axes[1, 0].bar(range(len(health_counts)), health_counts.values)
    axes[1, 0].set_xticks(range(len(health_counts)))
    axes[1, 0].set_xticklabels([s.split()[0] for s in health_counts.index], rotation=45)
    axes[1, 0].set_title('Health Status Distribution')
    axes[1, 0].set_ylabel('Count')
    
    # Plot 4: Age vs Risk Score
    axes[1, 1].scatter(df_classified['Age'], df_classified['Risk_Score'], alpha=0.5)
    axes[1, 1].set_title('Age vs Risk Score')
    axes[1, 1].set_xlabel('Age (years)')
    axes[1, 1].set_ylabel('Risk Score')
    
    plt.tight_layout()
    plt.savefig('data_visualization.png', dpi=100, bbox_inches='tight')
    print("✅ Saved visualization: data_visualization.png")
    
except ImportError:
    print("⚠️  Matplotlib not installed. Skipping visualizations.")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("WEEK 1-2 DATA PREPARATION COMPLETE ✅")
print("="*70)

print(f"""
Summary of Work Completed:
✅ Loaded {len(df)} blood count records
✅ Validated all parameters against medical ranges
✅ Classified parameters as Low/Normal/High
✅ Calculated risk scores for each patient
✅ Generated overall health status
✅ Saved processed data: {output_csv}
✅ Generated statistics: {stats_json}

Key Statistics:
  • Total Records: {stats['total_records']}
  • Normal Records: {stats['total_records'] - stats['abnormal_records']}
  • Abnormal Records: {stats['abnormal_records']}
  • Critical Records: {stats['critical_records']}
  • Average Risk Score: {stats['average_risk_score']:.3f}

Next Phase: Week 3-4 Pattern Recognition
  → Build Model 2: Risk Detection
  → Build Model 3: Contextual Analysis
  → Train ensemble of models on classified data
""")

print("="*70)
