import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import tempfile
import os
import re
from typing import Dict, Any, List

# =============================================================================
# MILESTONE 4 COMPLETE IMPLEMENTATION - ALL IN ONE FILE
# =============================================================================

st.set_page_config(page_title="🩺 Health Report Assistant - MILESTONE 4 FIXED", layout="wide")

class Model1_ParameterClassifier:
    def __init__(self):
        self.normal_ranges = {
            "Hemoglobin": (12.0, 16.0),
            "PlateletCount": (150000, 450000),
            "WhiteBloodCells": (4000, 11000)
        }

    def classify(self, params: Dict[str, float]) -> Dict[str, str]:
        classification = {}
        for param, value in params.items():
            if param in self.normal_ranges:
                low, high = self.normal_ranges[param]
                if value < low:
                    classification[param] = "LOW"
                elif value > high:
                    classification[param] = "HIGH"
                else:
                    classification[param] = "NORMAL"
        return classification

class Model2_RiskModel:
    def compute_risk(self, classifications: Dict[str, str]) -> Dict[str, Any]:
        risk_score = 0
        patterns = []

        if classifications.get("Hemoglobin") == "LOW":
            patterns.append("Anemia Risk")
            risk_score += 3
        if classifications.get("PlateletCount") == "LOW":
            patterns.append("Bleeding Risk")
            risk_score += 3
        if classifications.get("WhiteBloodCells") == "HIGH":
            patterns.append("Infection Risk")
            risk_score += 2

        risk_level = "HIGH" if risk_score >= 5 else "MODERATE" if risk_score >= 3 else "LOW"

        return {
            "score": risk_score,
            "level": risk_level,
            "patterns": patterns
        }

class Model3_ContextAnalyzer:
    def analyze(self, age: int, gender: str, risk: Dict[str, Any]) -> List[str]:
        context = []
        if age > 65:
            context.append("Elderly patient - higher clinical attention needed")
        if gender.lower() == "female" and "Anemia Risk" in risk["patterns"]:
            context.append("Consider menstrual/gestational factors")
        return context

class DataExtractor:
    @staticmethod
    def extract_csv_data(uploaded_file):
        """Extract first patient from CSV"""
        df = pd.read_csv(uploaded_file)
        row = df.iloc[0]
        return {
            "Age": int(row.get("Age", 50)),
            "Gender": str(row.get("Gender", "Unknown")),
            "Hemoglobin": float(row.get("Hemoglobin", 13.5)),
            "PlateletCount": float(row.get("PlateletCount", 250000)),
            "WhiteBloodCells": float(row.get("WhiteBloodCells", 8000))
        }

    @staticmethod
    def get_demo_data(patient_type: str):
        """Demo patients for testing"""
        demos = {
            "Anemia Patient": {"Age": 55, "Gender": "Male", "Hemoglobin": 10.8, "PlateletCount": 180000, "WhiteBloodCells": 7200},
            "Infection Patient": {"Age": 32, "Gender": "Female", "Hemoglobin": 12.9, "PlateletCount": 265000, "WhiteBloodCells": 14200},
            "Normal Patient": {"Age": 45, "Gender": "Male", "Hemoglobin": 14.2, "PlateletCount": 320000, "WhiteBloodCells": 6800}
        }
        return demos.get(patient_type, demos["Normal Patient"])

class ReportGenerator:
    DISCLAIMER = (
        "⚠️ **MEDICAL DISCLAIMER**: This is an AI-generated educational report. "
        "NOT a medical diagnosis. Consult a physician for clinical decisions. "
        "Uses conservative general guidelines only."
    )

    @staticmethod
    def generate_report(patient_data: Dict, classifications: Dict, risk: Dict, context: List[str]):
        findings = []
        for param, status in classifications.items():
            if status != "NORMAL":
                findings.append(f"{param}: {status}")

        summary = f"Patient Age {patient_data['Age']}, {patient_data['Gender']}. "
        if findings:
            summary += f"Abnormal: {', '.join(findings)}. "
        summary += f"Risk: {risk['level']} (score {risk['score']}/10). "
        if context:
            summary += "Context: " + "; ".join(context) + ". "

        recommendations = []
        if "Anemia Risk" in risk["patterns"]:
            recommendations.extend(["Iron-rich diet", "Follow-up CBC", "Ferritin test"])
        if "Bleeding Risk" in risk["patterns"]:
            recommendations.extend(["Avoid trauma", "Hematology consult"])
        if "Infection Risk" in risk["patterns"]:
            recommendations.extend(["Monitor symptoms", "Repeat CBC"])

        return {
            "patient": patient_data,
            "classifications": classifications,
            "risk": risk,
            "context": context,
            "summary": summary,
            "recommendations": recommendations[:5],
            "disclaimer": ReportGenerator.DISCLAIMER
        }

# =============================================================================
# STREAMLIT UI
# =============================================================================

st.title("🩺 Health Report Assistant - MILESTONE 4 ✅ FIXED")
st.markdown("*Complete AI Agent Workflow - All modules integrated*")

col1, col2 = st.columns(2)

with col1:
    st.header("📤 Input Data")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")

    user_query = st.text_area("Your question:", 
                            "Please analyze my blood test results.", height=60)

with col2:
    st.header("🧪 Quick Demo")
    demo_type = st.selectbox("Select demo patient:", 
                           ["Normal Patient", "Anemia Patient", "Infection Patient"])

if st.button("🚀 RUN FULL MILESTONE 4 WORKFLOW", type="primary", use_container_width=True):

    # Get patient data
    if uploaded_file is not None:
        patient_data = DataExtractor.extract_csv_data(uploaded_file)
        st.success("✅ CSV loaded successfully!")
    else:
        patient_data = DataExtractor.get_demo_data(demo_type)
        st.info(f"🧪 Using demo: {demo_type}")

    # Initialize models
    model1 = Model1_ParameterClassifier()
    model2 = Model2_RiskModel()
    model3 = Model3_ContextAnalyzer()

    with st.spinner("Running complete 4-model pipeline..."):
        # Full workflow
        classifications = model1.classify(patient_data)
        risk = model2.compute_risk(classifications)
        context = model3.analyze(patient_data["Age"], patient_data["Gender"], risk)
        report = ReportGenerator.generate_report(patient_data, classifications, risk, context)

    # Display Results
    st.header("📋 Generated Health Report")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Risk Score", f"{report['risk']['score']}/10")
    with c2:
        st.metric("Risk Level", report['risk']['level'])
    with c3:
        st.metric("Age", patient_data['Age'])

    st.subheader("🔬 Parameter Status")
    st.json(report['classifications'])

    st.subheader("📝 Clinical Summary")
    st.write(report['summary'])

    st.subheader("💡 Recommendations")
    for rec in report['recommendations']:
        st.success(f"• {rec}")

    st.subheader("⚠️ Medical Disclaimer")
    st.warning(report['disclaimer'])

    # Downloads
    st.subheader("💾 Download Report")
    df_report = pd.DataFrame([report['patient'] | {
        'risk_level': report['risk']['level'],
        'risk_score': report['risk']['score'],
        'summary': report['summary']
    }])

    csv = df_report.to_csv(index=False).encode()
    st.download_button("📥 Download CSV", csv, "milestone4_report.csv", "text/csv")

    json_str = json.dumps(report, indent=2, default=str)
    st.download_button("📥 Download JSON", json_str, "milestone4_report.json", "application/json")

st.markdown("---")
st.markdown("*Milestone 4 Complete: Full AI Agent Workflow ✅*")
