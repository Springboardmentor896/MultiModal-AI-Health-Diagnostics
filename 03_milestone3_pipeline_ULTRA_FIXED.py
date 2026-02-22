import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

print("=" * 80)
print("🚀 MILESTONE 3 RECOMMENDATION ENGINE - STARTING")
print("=" * 80)

class Model1_ParameterClassifier:
    def __init__(self):
        self.normal_ranges = {
            "Hemoglobin": (12.0, 16.0),
            "PlateletCount": (150000, 400000),
            "WhiteBloodCells": (4500, 11000)
        }

    def classify(self, params):
        classification = {}
        for param, value in params.items():
            if param in self.normal_ranges:
                low, high = self.normal_ranges[param]
                if value < low:
                    classification[param] = "Low"
                elif value > high:
                    classification[param] = "High"
                else:
                    classification[param] = "Normal"
        return classification

class Model2_PatternDetector:
    def detect_patterns(self, classifications):
        patterns = []
        risk_score = 0

        if classifications.get("WhiteBloodCells") == "High":
            patterns.append("Infection Risk")
            risk_score += 2

        if classifications.get("PlateletCount") == "Low":
            patterns.append("Bleeding Disorder")
            risk_score += 2

        if classifications.get("Hemoglobin") == "Low":
            patterns.append("Anemia")
            risk_score += 2

        return patterns, risk_score

class Model3_ContextAnalyzer:
    def add_context(self, age, gender, patterns):
        context_findings = []
        if age > 60 and "Anemia" in patterns:
            context_findings.append("Age-related anemia concern")
        return context_findings

class Model4_FindingsSynthesis:
    def __init__(self):
        self.templates = {
            "Hemoglobin": {
                "Low": "Low hemoglobin suggesting anemia",
                "High": "Elevated hemoglobin"
            },
            "PlateletCount": {
                "Low": "Low platelet count - bleeding risk",
                "High": "Elevated platelets"
            },
            "WhiteBloodCells": {
                "High": "Elevated white blood cells indicating infection",
                "Low": "Low white blood cells - immune suppression"
            }
        }

    def synthesize(self, classifications):
        findings = []
        for param, status in classifications.items():
            if param in self.templates and status in self.templates[param]:
                findings.append(self.templates[param][status])
        return "; ".join(findings) if findings else "None"

class Model5_RecommendationGenerator:
    def generate(self, findings, risk_score, age):
        recommendations = []
        follow_up = "2 weeks"

        if "anemia" in findings.lower():
            recommendations.extend([
                "Increase iron intake",
                "Vitamin B12 supplementation",
                "Medical consultation"
            ])

        if "bleeding risk" in findings.lower():
            recommendations.extend([
                "Avoid trauma",
                "Monitor for bleeding",
                "Hematology referral"
            ])

        if "infection" in findings.lower():
            recommendations.extend([
                "Monitor for fever",
                "Antibiotics if symptoms worsen",
                "Infectious disease consult"
            ])

        if risk_score >= 4:
            follow_up = "1 week"

        return recommendations[:5], len(recommendations), follow_up

class Model6_ReportGenerator:
    def generate_report(self, patient_data):
        return {
            "patient_id": patient_data["PatientID"],
            "age": patient_data["Age"],
            "gender": patient_data["Gender"],
            "risk_assessment": {
                "overall_risk": patient_data["RiskLevel"],
                "risk_score": patient_data["RiskScore"],
                "affected_systems": patient_data["AffectedSystems"].split(", ") if patient_data["AffectedSystems"] != "None" else []
            },
            "clinical_findings": patient_data["PrimaryFindings"],
            "recommendations": {
                "priority_actions": patient_data.get("PrimaryFindings", "").split("; ") if patient_data["PrimaryFindings"] != "None" else [],
                "follow_up": patient_data["FollowUpPeriod"]
            },
            "timestamp": datetime.now().isoformat()
        }

def main():
    try:
        if not os.path.exists("blood_count_dataset_FIXED.csv"):
            print("❌ ERROR: blood_count_dataset_FIXED.csv not found!")
            print("📥 Download both FIXED files from assistant")
            return

        df = pd.read_csv("blood_count_dataset_FIXED.csv")
        print(f"📂 Loading dataset from: blood_count_dataset_FIXED.csv")
        print(f"✓ Loaded {len(df)} patients")
        print(f"✓ Columns verified: {list(df.columns)}")

        required_cols = ["Age", "Gender", "Hemoglobin", "PlateletCount", "WhiteBloodCells"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ ERROR: Missing columns: {missing_cols}")
            return

    except Exception as e:
        print(f"❌ CSV Loading Error: {str(e)}")
        return

    model1 = Model1_ParameterClassifier()
    model2 = Model2_PatternDetector()
    model3 = Model3_ContextAnalyzer()
    model4 = Model4_FindingsSynthesis()
    model5 = Model5_RecommendationGenerator()
    model6 = Model6_ReportGenerator()

    results = []
    sample_reports = []

    print("\n⚙️  Processing patients through 6-model pipeline...")
    for i, row in df.iterrows():
        if i % 50 == 0:
            print(f"  ✓ Processed {i}/{len(df)} patients")

        params = {
            "Hemoglobin": row["Hemoglobin"],
            "PlateletCount": row["PlateletCount"],
            "WhiteBloodCells": row["WhiteBloodCells"]
        }

        classifications = model1.classify(params)
        patterns, risk_score = model2.detect_patterns(classifications)
        context = model3.add_context(row["Age"], row["Gender"], patterns)
        primary_findings = model4.synthesize(classifications)
        recs, rec_count, follow_up = model5.generate(primary_findings, risk_score, row["Age"])

        if risk_score >= 4:
            risk_level = "High"
            affected_systems = "Hematologic"
        elif risk_score >= 2:
            risk_level = "Moderate"
            affected_systems = "Immune"
        else:
            risk_level = "Low"
            affected_systems = "None"

        result = {
            "PatientID": i+1,
            "Age": row["Age"],
            "Gender": row["Gender"],
            "Hemoglobin": row["Hemoglobin"],
            "WBC": row["WhiteBloodCells"],
            "Platelets": row["PlateletCount"],
            "RiskLevel": risk_level,
            "RiskScore": round(risk_score, 1),
            "AffectedSystems": affected_systems,
            "PrimaryFindings": primary_findings,
            "RecommendationCount": rec_count,
            "FollowUpPeriod": follow_up
        }
        results.append(result)

        if i < 5:
            sample_reports.append(model6.generate_report(result))

    results_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"MILESTONE3_RECOMMENDATIONS_{timestamp}.csv"
    results_df.to_csv(csv_filename, index=False)

    json_filename = f"MILESTONE3_REPORTS_{timestamp}.json"
    with open(json_filename, "w") as f:
        json.dump(sample_reports, f, indent=2)

    print(f"\n✓ Processed {len(results)}/{len(df)} patients - COMPLETE")
    print(f"\n✅ CSV Output: {csv_filename}")
    print(f"   • Rows: {len(results_df)}")
    print(f"   • Columns: {len(results_df.columns)}")
    print(f"\n✅ JSON Output: {json_filename}")
    print(f"   • Sample reports: {len(sample_reports)}")

    risk_counts = results_df["RiskLevel"].value_counts()
    print(f"\n📊 PIPELINE STATISTICS:")
    print(f"   Total Patients: {len(results)}")
    for risk in ["High", "Moderate", "Low"]:
        count = risk_counts.get(risk, 0)
        pct = (count/len(results)*100)
        print(f"   {risk} Risk: {count} ({pct:.1f}%)")
    print(f"   Average Risk Score: {results_df['RiskScore'].mean():.1f}/10")
    print(f"   Average Recommendations: {results_df['RecommendationCount'].mean():.1f}")

    print(f"\n📋 SAMPLE OUTPUT (First 3 Patients):")
    sample_cols = ["PatientID", "Age", "Gender", "Hemoglobin", "WBC", "Platelets", 
                   "RiskLevel", "RiskScore", "AffectedSystems", "PrimaryFindings", 
                   "RecommendationCount", "FollowUpPeriod"]
    print(results_df[sample_cols].head(3).to_string(index=False))

    print("\n" + "=" * 80)
    print("✨ MILESTONE 3 PIPELINE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
