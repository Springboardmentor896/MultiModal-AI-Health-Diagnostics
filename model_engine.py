# model_engine.py
import re
import math
import numpy as np
import pandas as pd
from textwrap import shorten
from io import BytesIO

# PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# ----------------------
# Safe numeric helpers
# ----------------------
def as_num(x):
    try:
        if x is None:
            return np.nan
        if isinstance(x, (int, float, np.floating, np.integer)):
            return float(x)
        s = str(x).strip()
        m = re.search(r"[-+]?\d*\.?\d+", s)
        return float(m.group()) if m else np.nan
    except Exception:
        return np.nan

def _num(x):
    return as_num(x)


# ----------------------
# Feature engineering
# ----------------------
def compute_ratios(row):
    r = {}
    LDL = as_num(row.get("LDL_mg_dL", np.nan))
    HDL = as_num(row.get("HDL_mg_dL", np.nan))
    TC = as_num(row.get("Total_Cholesterol_mg_dL", np.nan))
    TG = as_num(row.get("Triglycerides_mg_dL", np.nan))

    if HDL and HDL > 0:
        r["TC_HDL_Ratio"] = (TC / HDL) if (not np.isnan(TC)) else np.nan
        r["LDL_HDL_Ratio"] = (LDL / HDL) if (not np.isnan(LDL)) else np.nan
    else:
        r["TC_HDL_Ratio"] = np.nan
        r["LDL_HDL_Ratio"] = np.nan

    if TG and HDL and TG > 0 and HDL > 0:
        try:
            r["Atherogenic_Index"] = float(math.log(TG / HDL))
        except Exception:
            r["Atherogenic_Index"] = np.nan
    else:
        r["Atherogenic_Index"] = np.nan

    # Bring through some baseline fields (if present)
    r["Fasting_Glucose_mg_dL"] = as_num(row.get("Fasting_Glucose_mg_dL", np.nan))
    r["Triglycerides_mg_dL"] = TG
    return r


# ----------------------
# Model 2: pattern detectors & risk scorers
# ----------------------
def detect_metabolic_syndrome_flags(row):
    flags = 0
    if as_num(row.get("Fasting_Glucose_mg_dL", np.nan)) >= 100:
        flags += 1
    if as_num(row.get("Triglycerides_mg_dL", np.nan)) >= 150:
        flags += 1
    if as_num(row.get("HDL_mg_dL", np.nan)) < 40:
        flags += 1
    if as_num(row.get("Waist_Circumference_cm", np.nan)) > 90:
        flags += 1
    return flags

def cardiovascular_risk_score(row):
    score = 0
    LDL = as_num(row.get("LDL_mg_dL", np.nan))
    HDL = as_num(row.get("HDL_mg_dL", np.nan))
    TG = as_num(row.get("Triglycerides_mg_dL", np.nan))
    sbp = as_num(row.get("Systolic_BP_mmHg", np.nan))
    crp = as_num(row.get("CRP_mg_L", np.nan))

    if LDL and LDL > 160: score += 3
    elif LDL and LDL > 130: score += 2
    if HDL and HDL < 40: score += 2
    if TG and TG > 200: score += 1
    if sbp and sbp > 140: score += 2
    if crp and crp > 3: score += 1
    return int(score)

def infection_severity_label(row):
    crp = as_num(row.get("CRP_mg_L", np.nan))
    pct = as_num(row.get("Procalcitonin_ng_mL", np.nan))
    d_dimer = as_num(row.get("D_Dimer_mg_L", np.nan))
    if (crp and crp > 100) or (pct and pct > 2) or (d_dimer and d_dimer > 2):
        return "High"
    if (crp and crp > 10) or (pct and pct > 0.5):
        return "Moderate"
    return "Low"

def liver_injury_flag(row):
    alt = as_num(row.get("ALT_U_L", np.nan))
    ast = as_num(row.get("AST_U_L", np.nan))
    tb = as_num(row.get("Total_Bilirubin_mg_dL", np.nan))
    if (alt and alt > 200) or (ast and ast > 200) or (tb and tb > 3):
        return True
    return False

def kidney_risk_stage(row):
    egfr = as_num(row.get("eGFR_mL_min_1_73m2", np.nan))
    if np.isnan(egfr): return None
    if egfr >= 90: return "G1"
    if egfr >= 60: return "G2"
    if egfr >= 30: return "G3"
    if egfr >= 15: return "G4"
    return "G5"


# ----------------------
# Model 3: contextual adjustments
# ----------------------
def contextual_adjustments(row, cv_score_col="Cardiovascular_Risk_Score"):
    adj = {}
    base = as_num(row.get(cv_score_col, np.nan))
    if np.isnan(base):
        base = 0
    age = as_num(row.get("Age", np.nan))
    gender_raw = row.get("Gender", "")
    gender = gender_raw.lower() if isinstance(gender_raw, str) else ""
    adj_score = base
    if age and age >= 60: adj_score += 1
    if gender == "male": adj_score += 1
    adj["Adjusted_Cardiovascular_Risk"] = int(adj_score) if not np.isnan(adj_score) else 0
    return adj


# ----------------------
# Integrator: run models on a DataFrame
# ----------------------
def run_models_on_df(df):
    df = df.copy().reset_index(drop=True)
    # compute ratios per-row
    ratio_series = df.apply(compute_ratios, axis=1)
    ratio_df = pd.DataFrame(list(ratio_series))
    df = pd.concat([df.reset_index(drop=True), ratio_df.reset_index(drop=True)], axis=1)

    # Model 2 outputs
    df["Metabolic_Syndrome_Flags"] = df.apply(detect_metabolic_syndrome_flags, axis=1)
    df["Cardiovascular_Risk_Score"] = df.apply(cardiovascular_risk_score, axis=1)
    df["Infection_Severity"] = df.apply(infection_severity_label, axis=1)
    df["Liver_Injury_Flag"] = df.apply(liver_injury_flag, axis=1)
    df["Kidney_Risk_Stage"] = df.apply(kidney_risk_stage, axis=1)

    # Model 3
    adj_df = df.apply(contextual_adjustments, axis=1, result_type="expand")
    df = pd.concat([df, adj_df], axis=1)

    return df


# ----------------------
# Synthesis + disease identification + recommendations
# ----------------------
def synthesize_findings(row):
    findings = []
    recommendations = []
    severity_score = 0
    suspected = []

    # cardiovascular
    cv = _num(row.get("Cardiovascular_Risk_Score", np.nan))
    if cv and cv > 4:
        suspected.append("High Cardiovascular Risk")
        findings.append("Elevated cardiovascular risk score.")
        recommendations.append("Consult cardiology; consider lipid-lowering therapy and lifestyle changes.")
        severity_score += 4

    # lipids
    tg = _num(row.get("Triglycerides_mg_dL", np.nan))
    ldl = _num(row.get("LDL_mg_dL", np.nan))
    hdl = _num(row.get("HDL_mg_dL", np.nan))
    if tg and tg > 200:
        suspected.append("Hypertriglyceridemia")
        findings.append(f"High triglycerides ({int(tg)} mg/dL).")
        recommendations.append("Reduce refined carbs & alcohol; increase activity; repeat lipid panel.")
        severity_score += 2
    if ldl and ldl >= 160:
        suspected.append("Severe Hypercholesterolemia")
        findings.append(f"Markedly elevated LDL ({int(ldl)} mg/dL).")
        recommendations.append("Consider statin therapy after clinical review.")
        severity_score += 3
    if hdl and hdl < 40:
        suspected.append("Low HDL Syndrome")
        findings.append(f"Low HDL ({int(hdl)} mg/dL).")
        recommendations.append("Increase physical activity and healthy fats (e.g., oily fish).")
        severity_score += 1

    # liver
    if row.get("Liver_Injury_Flag"):
        suspected.append("Probable Liver Injury")
        findings.append("Abnormal transaminases / bilirubin suggest liver injury.")
        recommendations.append("Immediate clinical review; repeat LFTs and review medications/toxins.")
        severity_score += 4

    # kidney
    kstage = row.get("Kidney_Risk_Stage")
    if isinstance(kstage, str) and kstage in ("G4", "G5"):
        suspected.append("Advanced Chronic Kidney Disease")
        findings.append(f"Reduced kidney function (stage {kstage}).")
        recommendations.append("Urgent nephrology referral; review medications and BP control.")
        severity_score += 4
    elif isinstance(kstage, str) and kstage.startswith("G"):
        suspected.append("Reduced Kidney Function")
        findings.append(f"Estimated kidney stage: {kstage}.")
        recommendations.append("Consider urine albumin testing and BP optimization.")
        severity_score += 1

    # infection / inflammation
    inf = str(row.get("Infection_Severity", "")).lower()
    crp = _num(row.get("CRP_mg_L", np.nan))
    if inf == "high" or (crp and crp > 100):
        suspected.append("Severe Infection / Systemic Inflammation")
        findings.append(f"High inflammation markers (CRP {crp}).")
        recommendations.append("Urgent evaluation and targeted microbial testing as indicated.")
        severity_score += 4
    elif inf == "moderate" or (crp and crp > 10):
        suspected.append("Inflammation")
        findings.append(f"Moderate inflammatory markers (CRP {crp}).")
        recommendations.append("Clinical correlation and repeat tests recommended.")
        severity_score += 2

    # anemia
    hb = _num(row.get("Hemoglobin_g_dL", np.nan))
    if hb and hb < 11:
        suspected.append("Anemia")
        findings.append(f"Low hemoglobin ({hb} g/dL).")
        recommendations.append("Check iron studies, B12/folate; evaluate for blood loss.")
        severity_score += 2

    # vitamin D
    vitd = _num(row.get("Vitamin_D_ng_mL", np.nan))
    if vitd and vitd < 20:
        suspected.append("Vitamin D Deficiency")
        findings.append(f"Low Vitamin D ({int(vitd)} ng/mL).")
        recommendations.append("Consider supplementation per local guidelines.")
        severity_score += 1

    # finalize severity
    if severity_score >= 8:
        severity = "high"
    elif severity_score >= 4:
        severity = "moderate"
    else:
        severity = "low"

    if not findings:
        findings_paragraph = "No significant flagged findings identified by automated screens."
    else:
        bullets = [f for f in findings]
        findings_paragraph = " | ".join(bullets[:7])

    return {
        "findings_list": findings,
        "findings_paragraph": findings_paragraph,
        "overall_severity": severity,
        "suspected_diseases": ", ".join(sorted(set(suspected))) if suspected else "None identified",
        "recommendations_list": recommendations if recommendations else ["No recommendations generated."]
    }

def synthesize_and_recommend_df(df):
    rows = []
    for _, row in df.iterrows():
        s = synthesize_findings(row)
        merged = {**row.to_dict()}
        merged.update({
            "Findings_Paragraph": s["findings_paragraph"],
            "Overall_Severity": s["overall_severity"],
            "Suspected_Diseases": s["suspected_diseases"],
            "Recommendations_Structured": [{"finding": f, "recommendation": r} for f, r in zip(s["findings_list"], s["recommendations_list"])] if s["recommendations_list"] else []
        })
        rows.append(merged)
    return pd.DataFrame(rows)


# ----------------------
# OCR text parser (used by the Streamlit app)
# ----------------------
def parse_parameters(text: str) -> dict:
    """
    Permissive regex-based parser for common lab report labels.
    Returns a dict of extracted values (numeric fields converted where possible).
    """
    def extract_numeric(label_variants):
        for label in label_variants:
            p = rf"{re.escape(label)}[^\d\n\r\-]*[:\-]?\s*([-+]?\d*\.?\d+)"
            m = re.search(p, text, re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1))
                except:
                    pass
        return np.nan

    def extract_text(label_variants):
        for label in label_variants:
            p = rf"{re.escape(label)}[^\n\r:]*[:\-]?\s*([^\n\r]+)"
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""

    out = {}
    # Demographics
    out["Patient_ID"] = extract_text(["Patient ID", "Patient No", "Patient Number"])
    out["Patient_Name"] = extract_text(["Patient Name", "Name"])
    age = extract_numeric(["Age"])
    out["Age"] = int(age) if not np.isnan(age) else np.nan
    out["Gender"] = extract_text(["Gender", "Sex"])

    # Hematology
    out["Hemoglobin_g_dL"] = extract_numeric(["Hemoglobin", r"\bHb\b"])
    out["WBC_cells_uL"] = extract_numeric(["WBC", "White Blood Cells", "WBC cells"])
    out["Platelets_lakh_uL"] = extract_numeric(["Platelets", "Platelet"])
    out["Hematocrit_percent"] = extract_numeric(["Hematocrit", "Hct"])

    # Iron/vitamins
    out["Serum_Iron_ug_dL"] = extract_numeric(["Serum Iron"])
    out["Serum_Ferritin_ng_mL"] = extract_numeric(["Serum Ferritin", "Ferritin"])
    out["Vitamin_B12_pg_mL"] = extract_numeric(["Vitamin B12", r"\bB12\b"])
    out["Folate_ng_mL"] = extract_numeric(["Folate"])

    # Biochemistry / liver
    out["ALT_U_L"] = extract_numeric(["ALT", "SGPT"])
    out["AST_U_L"] = extract_numeric(["AST", "SGOT"])
    out["Total_Bilirubin_mg_dL"] = extract_numeric(["Total Bilirubin", "Bilirubin", r"\bT\.Bili\b"])

    # Kidney
    out["Serum_Creatinine_mg_dL"] = extract_numeric(["Serum Creatinine", "Creatinine"])
    out["eGFR_mL_min_1_73m2"] = extract_numeric(["eGFR", "eGFR mL"])

    # Lipids / glucose
    out["Total_Cholesterol_mg_dL"] = extract_numeric(["Total Cholesterol", "Cholesterol"])
    out["LDL_mg_dL"] = extract_numeric(["LDL"])
    out["HDL_mg_dL"] = extract_numeric(["HDL"])
    out["Triglycerides_mg_dL"] = extract_numeric(["Triglycerides", "Triglyceride", r"\bTG\b"])
    out["Fasting_Glucose_mg_dL"] = extract_numeric(["Fasting Glucose", "Glucose", "Fasting Blood Sugar", "FBS"])
    out["HbA1c_percent"] = extract_numeric(["HbA1c", "A1c"])

    # Inflammation
    out["CRP_mg_L"] = extract_numeric(["CRP", "C-reactive protein"])
    out["Procalcitonin_ng_mL"] = extract_numeric(["Procalcitonin", "PCT"])
    out["D_Dimer_mg_L"] = extract_numeric(["D-Dimer", "D Dimer"])

    # Misc textual fields
    out["Peripheral_Smear_Result"] = extract_text(["Peripheral Smear Result", "Peripheral Smear"])
    out["Provisional_Diagnosis"] = extract_text(["Provisional Diagnosis", "Diagnosis"])
    out["Fasting_Status"] = extract_text(["Fasting Status", "Fasting"])

    return out


# ----------------------
# Simple PDF generator (returns bytes)
# ----------------------
def generate_pdf_bytes_from_row(row) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>Personalized Health Recommendation Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Findings
    findings = row.get("Findings_Paragraph", "No findings available.")
    story.append(Paragraph("<b>Synthesized Findings</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(findings, styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Suspected diseases
    s_d = row.get("Suspected_Diseases", row.get("suspected_diseases", "None identified"))
    story.append(Paragraph(f"<b>Identified Conditions:</b> {s_d}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Overall severity
    severity = row.get("Overall_Severity", "unknown").capitalize()
    story.append(Paragraph(f"<b>Overall Severity:</b> {severity}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Recommendations
    recs = row.get("Recommendations_Structured") or row.get("recommendations_list") or []
    if isinstance(recs, list) and recs:
        story.append(Paragraph("<b>Personalized Recommendations</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        rec_items = []
        # recs may be list of dicts or list of strings
        if all(isinstance(r, dict) and "recommendation" in r for r in recs):
            for r in recs:
                txt = f"<b>Finding:</b> {r.get('finding','')}<br/><b>Recommendation:</b> {r.get('recommendation','')}<br/><b>Urgency:</b> {r.get('urgency','routine').capitalize()}"
                rec_items.append(ListItem(Paragraph(txt, styles["BodyText"])))
        else:
            # fallback: treat as plain list
            for r in recs:
                rec_items.append(ListItem(Paragraph(str(r), styles["BodyText"])))
        story.append(ListFlowable(rec_items, bulletType="bullet"))
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("<b>Personalized Recommendations</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("No recommendations generated.", styles["BodyText"]))
        story.append(Spacer(1, 12))

    # Disclaimer
    story.append(Paragraph("<b>Disclaimer</b>", styles["Heading3"]))
    story.append(Paragraph(
        "This report is generated by an automated system for research and educational purposes only. "
        "It does not replace professional medical advice. Always consult a qualified healthcare provider.",
        styles["BodyText"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

