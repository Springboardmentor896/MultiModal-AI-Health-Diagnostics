"""
FILE: 03_milestone3_pipeline.py (FIXED VERSION)
PURPOSE: Complete Milestone 3 Pipeline - Orchestrate Models 1-6 for all patients
STATUS: Fixed & Production Ready
DESCRIPTION: End-to-end pipeline processing 500 patients through entire recommendation workflow

✅ FIXED: Column name mismatch (WBC instead of WhiteBloodCells)
"""

import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any

# ============================================================================
# FIXED: Column name mapping for CSV compatibility
# ============================================================================
COLUMN_MAPPING = {
    'Age': 'Age',
    'Gender': 'Gender',
    'Hemoglobin': 'Hemoglobin',
    'WBC': 'WBC',  # FIXED: Was 'WhiteBloodCells', now 'WBC'
    'Platelets': 'Platelets'  # FIXED: Was 'PlateletCount', now 'Platelets'
}

class Model1ParameterInterpreter:
    """Classifies blood parameters as High/Low/Normal."""
    
    def __init__(self):
        self.normal_ranges = {
            "Hemoglobin": (12.0, 16.0),
            "WBC": (4500, 11000),  # FIXED: Was WhiteBloodCells
            "Platelets": (150000, 400000)  # FIXED: Was PlateletCount
        }
    
    def interpret(self, hemoglobin, wbc, platelets):
        return {
            "Hemoglobin": "Low" if hemoglobin < self.normal_ranges["Hemoglobin"][0] else 
                         "High" if hemoglobin > self.normal_ranges["Hemoglobin"][1] else "Normal",
            "WBC": "Low" if wbc < self.normal_ranges["WBC"][0] else 
                   "High" if wbc > self.normal_ranges["WBC"][1] else "Normal",  # FIXED
            "Platelets": "Low" if platelets < self.normal_ranges["Platelets"][0] else 
                        "High" if platelets > self.normal_ranges["Platelets"][1] else "Normal"  # FIXED
        }


class Model2PatternEngine:
    """Detects medical patterns and calculates risk."""
    
    def detect_patterns(self, params):
        patterns = []
        risk_score = 0
        
        if params.get("Hemoglobin") == "Low":
            patterns.append("Anemia Risk")
            risk_score += 2
        if params.get("WBC") == "High":  # FIXED
            patterns.append("Infection Risk")
            risk_score += 2
        if params.get("Platelets") == "Low":  # FIXED
            patterns.append("Bleeding Disorder")
            risk_score += 2
        
        return {
            "patterns": patterns,
            "risk_score": min(risk_score, 10),
            "risk_level": "Low" if risk_score <= 2 else "Moderate" if risk_score <= 5 else "High"
        }


class Model3ContextEngine:
    """Adds age/gender context."""
    
    @staticmethod
    def get_age_group(age):
        if age <= 35: return "YOUNG"
        elif age <= 50: return "MIDDLE"
        elif age <= 65: return "SENIOR"
        else: return "ELDERLY"
    
    def process(self, age, gender):
        return {
            "age": age,
            "gender": gender,
            "age_group": self.get_age_group(age)
        }


class Model4FindingsSynthesisEngine:
    """Synthesizes findings into clinical narrative."""
    
    def __init__(self):
        self.finding_templates = {
            "Hemoglobin": {
                "Low": "Low hemoglobin suggesting anemia",
                "High": "Elevated hemoglobin",
                "Normal": None
            },
            "WBC": {  # FIXED
                "Low": "Reduced white blood cells",
                "High": "Elevated white blood cells indicating infection",
                "Normal": None
            },
            "Platelets": {  # FIXED
                "Low": "Low platelet count - bleeding risk",
                "High": "Elevated platelet count",
                "Normal": None
            }
        }
    
    def synthesize(self, model1, model2, model3=None):
        findings = []
        for param, status in model1.items():
            if param in self.finding_templates and status in self.finding_templates[param]:
                finding = self.finding_templates[param][status]
                if finding:
                    findings.append(finding)
        
        return {
            "key_findings": findings,
            "detected_patterns": model2.get("patterns", []),
            "overall_risk": model2.get("risk_level", "Unknown"),
            "affected_systems": self._get_systems(model2.get("patterns", [])),
            "risk_score": model2.get("risk_score", 0)
        }
    
    @staticmethod
    def _get_systems(patterns):
        system_map = {
            "Anemia Risk": "Hematologic",
            "Infection Risk": "Immune",
            "Bleeding Disorder": "Hematologic"
        }
        return list(set([system_map.get(p, "Other") for p in patterns]))


class Model5RecommendationGenerator:
    """Generates personalized recommendations."""
    
    def __init__(self):
        self.rules = {
            "Low hemoglobin suggesting anemia": {
                "actions": ["Increase iron intake", "Vitamin B12 supplementation"],
                "tests": ["Ferritin test", "Serum iron"],
                "follow_up": "2 weeks"
            },
            "Elevated white blood cells indicating infection": {
                "actions": ["Medical consultation", "Monitor vital signs"],
                "tests": ["Blood culture", "Urinalysis"],
                "follow_up": "1 week"
            },
            "Low platelet count - bleeding risk": {
                "actions": ["Avoid trauma", "Medical consultation"],
                "tests": ["Platelet count trend"],
                "follow_up": "1 week"
            }
        }
    
    def generate(self, findings):
        actions = []
        tests = []
        max_follow_up = "2 weeks"
        
        for finding in findings:
            if finding in self.rules:
                rule = self.rules[finding]
                actions.extend(rule.get("actions", []))
                tests.extend(rule.get("tests", []))
        
        return {
            "priority_actions": list(set(actions)),
            "required_tests": list(set(tests)),
            "follow_up_period": max_follow_up,
            "total_recommendations": len(actions) + len(tests)
        }


class Model6ComprehensiveReportGenerator:
    """Generates professional medical report."""
    
    @staticmethod
    def generate_report(patient_id, age, gender, model1, model4, model5, recommendations):
        return {
            "patient_id": patient_id,
            "age": age,
            "gender": gender,
            "risk_assessment": {
                "overall_risk": model4.get("overall_risk"),
                "risk_score": model4.get("risk_score"),
                "affected_systems": model4.get("affected_systems")
            },
            "clinical_findings": model4.get("key_findings"),
            "recommendations": {
                "priority_actions": recommendations.get("priority_actions"),
                "required_tests": recommendations.get("required_tests"),
                "follow_up": recommendations.get("follow_up_period")
            },
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# MILESTONE 3 PIPELINE - MAIN EXECUTION (FIXED)
# ============================================================================

class Milestone3Pipeline:
    """Complete end-to-end Milestone 3 recommendation pipeline."""
    
    def __init__(self):
        """Initialize all 6 models."""
        self.model1 = Model1ParameterInterpreter()
        self.model2 = Model2PatternEngine()
        self.model3 = Model3ContextEngine()
        self.model4 = Model4FindingsSynthesisEngine()
        self.model5 = Model5RecommendationGenerator()
        self.model6 = Model6ComprehensiveReportGenerator()
    
    def process_patient(self, patient_id, row):
        """
        Process single patient through all 6 models.
        
        Args:
            patient_id: Patient ID
            row: Patient data row with Age, Gender, Hemoglobin, WBC, Platelets
            
        Returns:
            Complete patient recommendation report
        """
        
        try:
            # Extract patient data with FIXED column names
            age = row['Age']
            gender = row['Gender']
            hemoglobin = row['Hemoglobin']
            wbc = row['WBC']  # FIXED: Now uses 'WBC'
            platelets = row['Platelets']  # FIXED: Now uses 'Platelets'
            
            # MODEL 1: Interpret parameters
            model1_output = self.model1.interpret(hemoglobin, wbc, platelets)
            
            # MODEL 2: Detect patterns
            model2_output = self.model2.detect_patterns(model1_output)
            
            # MODEL 3: Add context
            model3_output = self.model3.process(age, gender)
            
            # MODEL 4: Synthesize findings
            model4_output = self.model4.synthesize(model1_output, model2_output, model3_output)
            
            # MODEL 5: Generate recommendations
            model5_output = self.model5.generate(model4_output.get("key_findings", []))
            
            # MODEL 6: Create comprehensive report
            report = self.model6.generate_report(
                patient_id, age, gender, 
                model1_output, model4_output, 
                model5_output, model5_output
            )
            
            return report
            
        except Exception as e:
            print(f"❌ Error processing patient {patient_id}: {str(e)}")
            return None
    
    def process_all_patients(self, csv_file):
        """
        Process all patients from CSV file.
        
        Args:
            csv_file: Path to blood_count_dataset.csv
            
        Returns:
            Tuple of (results_dataframe, sample_reports_json)
        """
        
        print("\n" + "="*80)
        print("🚀 MILESTONE 3 RECOMMENDATION ENGINE - STARTING")
        print("="*80)
        
        # Load dataset
        print(f"\n📂 Loading dataset from: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            print(f"❌ ERROR: File '{csv_file}' not found!")
            print("   Please ensure blood_count_dataset.csv is in the same directory.")
            return None, None
        
        # Verify columns exist (FIXED: Check for correct column names)
        required_columns = ['Age', 'Gender', 'Hemoglobin', 'WBC', 'Platelets']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"\n❌ ERROR: Missing columns: {missing_columns}")
            print(f"   Available columns: {list(df.columns)}")
            print("\n   Your CSV should have these columns:")
            for col in required_columns:
                print(f"     - {col}")
            return None, None
        
        print(f"✓ Loaded {len(df)} patients")
        print(f"✓ Columns verified: {', '.join(required_columns)}")
        
        # Process each patient
        print("\n⚙️  Processing patients through 6-model pipeline...")
        reports = []
        results = []
        
        for idx, row in df.iterrows():
            patient_id = idx + 1
            
            # Process patient
            report = self.process_patient(patient_id, row)
            
            if report:  # Only add if successful
                reports.append(report)
                
                # Create summary row for CSV
                result_row = {
                    'PatientID': patient_id,
                    'Age': row['Age'],
                    'Gender': row['Gender'],
                    'Hemoglobin': row['Hemoglobin'],
                    'WBC': row['WBC'],  # FIXED
                    'Platelets': row['Platelets'],  # FIXED
                    'RiskLevel': report['risk_assessment']['overall_risk'],
                    'RiskScore': report['risk_assessment']['risk_score'],
                    'AffectedSystems': ', '.join(report['risk_assessment']['affected_systems']),
                    'PrimaryFindings': '; '.join(report['clinical_findings'][:2]) if report['clinical_findings'] else 'None',
                    'RecommendationCount': len(report['recommendations']['priority_actions']),
                    'FollowUpPeriod': report['recommendations']['follow_up']
                }
                results.append(result_row)
            
            # Progress indicator
            if (idx + 1) % 50 == 0:
                print(f"  ✓ Processed {idx + 1}/{len(df)} patients")
        
        print(f"  ✓ Processed {len(results)}/{len(df)} patients - COMPLETE")
        
        # Create results dataframe
        results_df = pd.DataFrame(results)
        
        # Generate output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_output = f"MILESTONE3_RECOMMENDATIONS_{timestamp}.csv"
        results_df.to_csv(csv_output, index=False)
        print(f"\n✅ CSV Output: {csv_output}")
        print(f"   • Rows: {len(results_df)}")
        print(f"   • Columns: {len(results_df.columns)}")
        
        # Save JSON samples (first 5 detailed reports)
        json_output = f"MILESTONE3_REPORTS_{timestamp}.json"
        sample_reports = reports[:5]
        with open(json_output, 'w') as f:
            json.dump(sample_reports, f, indent=2)
        print(f"\n✅ JSON Output: {json_output}")
        print(f"   • Sample reports: {len(sample_reports)}")
        print(f"   • Format: Physician-ready detailed reports")
        
        # Print statistics
        self.print_statistics(results_df)
        
        print("\n" + "="*80)
        print("✨ MILESTONE 3 PIPELINE COMPLETE")
        print("="*80 + "\n")
        
        return results_df, sample_reports


    @staticmethod
    def print_statistics(df):
        """Print summary statistics."""
        print("\n📊 PIPELINE STATISTICS:")
        print(f"   Total Patients: {len(df)}")
        print(f"   High Risk: {len(df[df['RiskLevel'] == 'High'])} ({len(df[df['RiskLevel'] == 'High'])/len(df)*100:.1f}%)")
        print(f"   Moderate Risk: {len(df[df['RiskLevel'] == 'Moderate'])} ({len(df[df['RiskLevel'] == 'Moderate'])/len(df)*100:.1f}%)")
        print(f"   Low Risk: {len(df[df['RiskLevel'] == 'Low'])} ({len(df[df['RiskLevel'] == 'Low'])/len(df)*100:.1f}%)")
        print(f"   Average Risk Score: {df['RiskScore'].mean():.1f}/10")
        print(f"   Average Recommendations: {df['RecommendationCount'].mean():.1f}")


# ============================================================================
# EXECUTE PIPELINE
# ============================================================================

if __name__ == "__main__":
    # Initialize pipeline
    pipeline = Milestone3Pipeline()
    
    # Process all patients
    # Make sure blood_count_dataset.csv exists in same directory
    csv_file = "blood_count_dataset.csv"
    
    try:
        results_df, sample_reports = pipeline.process_all_patients(csv_file)
        
        if results_df is not None:
            # Display sample output
            print("\n📋 SAMPLE OUTPUT (First 3 Patients):")
            print(results_df.head(3).to_string())
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        print("   Please check your CSV file and try again.")
