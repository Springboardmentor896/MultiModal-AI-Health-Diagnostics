# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import requests
import json

# Try importing your model engine. If parts are missing, the app will use safe fallbacks.
try:
    from model_engine import (
        run_models_on_df,
        synthesize_and_recommend_df,
        parse_parameters,
        generate_pdf_bytes_from_row,
    )
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_ERROR = str(e)
    # --- Minimal fallback implementations so the UI still runs ---
    def parse_parameters(text: str) -> dict:
        """
        Permissive OCR parser fallback (extracts a few common numeric fields).
        Not clinical-grade. Use model_engine.py for full features.
        """
        import re

        def extract_numeric(labels):
            for lab in labels:
                m = re.search(rf"{re.escape(lab)}[^\d\.\-]*([\-+]?\d*\.?\d+)", text, re.IGNORECASE)
                if m:
                    try:
                        return float(m.group(1))
                    except:
                        pass
            return np.nan

        def extract_text(labels):
            for lab in labels:
                m = re.search(rf"{re.escape(lab)}[^\n\r:]*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
            return ""

        out = {}
        out["Patient_ID"] = extract_text(["Patient ID", "Patient No", "Patient Number"])
        out["Patient_Name"] = extract_text(["Patient Name", "Name"])
        age = extract_numeric(["Age"])
        out["Age"] = int(age) if not np.isnan(age) else np.nan
        out["Gender"] = extract_text(["Gender", "Sex"])

        out["Hemoglobin_g_dL"] = extract_numeric(["Hemoglobin", r"\bHb\b"])
        out["Triglycerides_mg_dL"] = extract_numeric(["Triglycerides", "TG"])
        out["LDL_mg_dL"] = extract_numeric(["LDL"])
        out["HDL_mg_dL"] = extract_numeric(["HDL"])
        out["CRP_mg_L"] = extract_numeric(["CRP", "C-reactive protein"])
        out["eGFR_mL_min_1_73m2"] = extract_numeric(["eGFR"])

        # small hints fields
        out["Peripheral_Smear_Result"] = extract_text(["Peripheral Smear Result", "Peripheral Smear"])
        out["Provisional_Diagnosis"] = extract_text(["Provisional Diagnosis", "Diagnosis"])
        return out

    def run_models_on_df(df):
        """
        Very small fallback that returns the df with minimal synthetic columns
        so downstream synthesize function can run.
        """
        df = df.copy()
        # ensure numeric conversion
        df["Triglycerides_mg_dL"] = pd.to_numeric(df.get("Triglycerides_mg_dL"), errors="coerce")
        df["LDL_mg_dL"] = pd.to_numeric(df.get("LDL_mg_dL"), errors="coerce")
        df["HDL_mg_dL"] = pd.to_numeric(df.get("HDL_mg_dL"), errors="coerce")
        # Tiny heuristic scores
        def cardio_score(r):
            s = 0
            if pd.notna(r.get("LDL_mg_dL")) and r.get("LDL_mg_dL") > 160: s += 3
            elif pd.notna(r.get("LDL_mg_dL")) and r.get("LDL_mg_dL") > 130: s += 2
            if pd.notna(r.get("HDL_mg_dL")) and r.get("HDL_mg_dL") < 40: s += 2
            if pd.notna(r.get("Triglycerides_mg_dL")) and r.get("Triglycerides_mg_dL") > 200: s += 1
            return s

        df["Cardiovascular_Risk_Score"] = df.apply(cardio_score, axis=1)
        # set defaults
        df["Infection_Severity"] = df.get("CRP_mg_L").apply(lambda x: "High" if pd.notna(x) and x > 100 else ("Moderate" if pd.notna(x) and x > 10 else "Low")) if "CRP_mg_L" in df else "Low"
        df["Liver_Injury_Flag"] = False
        df["Kidney_Risk_Stage"] = None
        df["Metabolic_Syndrome_Flags"] = 0
        df["TC_HDL_Ratio"] = np.nan
        return df

    def synthesize_and_recommend_df(df):
        """
        Minimal synthesizer that creates Findings_Paragraph, Recommendations_Structured, Overall_Severity.
        """
        rows = []
        for _, r in df.iterrows():
            findings = []
            severity_score = 0
            tg = r.get("Triglycerides_mg_dL")
            if pd.notna(tg) and tg > 200:
                findings.append(("high_tg", f"High triglycerides ({int(tg)} mg/dL)"))
                severity_score += 1
            ldl = r.get("LDL_mg_dL")
            if pd.notna(ldl) and ldl >= 160:
                findings.append(("high_ldl", f"Markedly elevated LDL ({int(ldl)} mg/dL)"))
                severity_score += 3
            cv = r.get("Cardiovascular_Risk_Score", 0)
            if cv and cv > 0:
                findings.append(("cv_score", f"Cardiovascular Risk score: {int(cv)}"))
                severity_score += int(cv)
            if severity_score >= 8:
                sev = "high"
            elif severity_score >= 4:
                sev = "moderate"
            else:
                sev = "low"
            paragraph = " | ".join([f[1] for f in findings]) if findings else "No significant findings detected."
            # recommendations simple mapping
            recs = []
            for code, text in findings:
                if code in ("high_tg", "high_ldl", "cv_score"):
                    recs.append({
                        "finding_code": code,
                        "finding_text": text,
                        "recommendation": ("Lifestyle: reduce saturated fats and trans fats, increase dietary fiber and oily fish; "
                                           "Exercise: aim for 150 min/week. Follow-up: repeat lipid panel in 6-12 weeks."),
                        "urgency": "routine"
                    })
            rows.append({**r.to_dict(), "Findings_Paragraph": paragraph, "Recommendations_Structured": recs, "Overall_Severity": sev})
        return pd.DataFrame(rows)

    def generate_pdf_bytes_from_row(row):
        """
        Very small PDF generator fallback (ReportLab) — returns bytes.
        """
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
        except Exception:
            return b""

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []
        # Title
        story.append(Paragraph("<b>Personalized Health Recommendation Report</b>", styles["Title"]))
        story.append(Spacer(1, 12))
        # ensure dict
        if hasattr(row, "to_dict"):
            data = row.to_dict()
        elif isinstance(row, dict):
            data = row
        else:
            data = {}

        story.append(Paragraph("<b>Synthesized Findings</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(data.get("Findings_Paragraph", "No findings."), styles["BodyText"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Overall Severity:</b> {data.get('Overall_Severity','unknown').capitalize()}", styles["BodyText"]))
        story.append(Spacer(1, 12))

        recs = data.get("Recommendations_Structured", [])
        if recs:
            story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
            story.append(Spacer(1, 6))
            items = []
            for r in recs:
                text = f"<b>Finding:</b> {r.get('finding_text','')}<br/><b>Recommendation:</b> {r.get('recommendation','')}<br/><b>Urgency:</b> {r.get('urgency','routine').capitalize()}"
                items.append(ListItem(Paragraph(text, styles["BodyText"])))
            story.append(ListFlowable(items, bulletType="bullet"))
            story.append(Spacer(1, 12))

        story.append(Paragraph("<b>Disclaimer</b>", styles["Heading3"]))
        story.append(Paragraph("This report is generated by an automated system for research and educational purposes only. It does not replace professional medical advice.", styles["BodyText"]))
        doc.build(story)
        buf.seek(0)
        return buf.read()


# -------------------------
# page config and session
# -------------------------
st.set_page_config(page_title="AI Health Diagnostics", page_icon="🩺", layout="wide")

if "report_row" not in st.session_state:
    st.session_state["report_row"] = None
if "pdf" not in st.session_state:
    st.session_state["pdf"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --------------------------------------------------
# STYLING (dark theme you liked)
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background: #0b0f12; color:#e6eef2; }
.card {
    background:#0f1316;
    border:1px solid rgba(255,255,255,0.04);
    padding:18px;
    border-radius:12px;
}
.badge {
    padding:6px 10px;
    border-radius:999px;
    font-weight:600;
    font-size:12px;
}
.badge-low { background:#1f2a32; color:#a7d6a6; }
.badge-moderate { background:#2a2320; color:#f4c47a; }
.badge-high { background:#3a1a1d; color:#ff8b94; }
.rec-card {
    background:#0b0f12;
    border-radius:10px;
    padding:14px;
    margin-bottom:10px;
    border:1px solid rgba(255,255,255,0.03);
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🩺 Multi-Model AI Health Diagnostics")
st.caption("Upload a scanned lab PDF or image")

if IMPORT_ERROR:
    st.warning("Partial import error from model_engine.py. The app will use a fallback analyzer. For full features put a working model_engine.py in the project directory.")
    st.code(IMPORT_ERROR)

st.divider()

# --------------------------------------------------
# FILE UPLOAD (PDF or image)
# --------------------------------------------------
uploaded_file = st.file_uploader("Upload PDF / Image", type=["pdf", "png", "jpg", "jpeg"], key="file_uploader")
if not uploaded_file:
    st.info("Upload a scanned lab PDF or image to begin.")
    st.stop()

file_bytes = uploaded_file.read()
file_name = uploaded_file.name.lower()

# OCR extraction (guarded)
extracted_text = ""
try:
    if file_name.endswith(".pdf"):
        images = convert_from_bytes(file_bytes)
        for img in images:
            extracted_text += pytesseract.image_to_string(img)
    else:
        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        extracted_text = pytesseract.image_to_string(image)
except Exception as e:
    st.error(f"OCR failed: {e}")
    st.stop()

# non-empty label to avoid Streamlit warnings
st.markdown("### OCR Output (Editable)")
txt_area_val = st.text_area("OCR Output (edit if needed)", extracted_text, height=300, key="ocr_text")

# Right-aligned Run button
col1, col2, col3 = st.columns([6, 1, 2])
with col3:
    run_clicked = st.button("✨ Run Report", key="run_report_btn", use_container_width=True)

if run_clicked:
    if not txt_area_val.strip():
        st.error("No readable text detected.")
    else:
        with st.spinner("Parsing and running models..."):
            try:
                parsed = parse_parameters(txt_area_val)
                df_single = pd.DataFrame([parsed])

                # Ensure minimal columns exist to avoid exceptions in models
                for col in ["Cardiovascular_Risk_Score", "Adjusted_Cardiovascular_Risk", "Metabolic_Syndrome_Flags",
                            "Infection_Severity", "Liver_Injury_Flag", "Kidney_Risk_Stage", "TC_HDL_Ratio"]:
                    if col not in df_single.columns:
                        df_single[col] = "Low" if col == "Infection_Severity" else 0

                df_processed = run_models_on_df(df_single)
                df_m3 = synthesize_and_recommend_df(df_processed)
                # convert to plain dict for stable session storage
                row0_series = df_m3.iloc[0]
                st.session_state["report_row"] = row0_series.to_dict()
                st.session_state["pdf"] = None  # clear previous pdf
                st.success("Report ready — preview below.")
            except Exception as e:
                st.error(f"Model processing failed: {e}")
                st.session_state["report_row"] = None

# -----------------------
# Preview (only when present)
# -----------------------
if st.session_state.get("report_row") is not None:
    row = st.session_state["report_row"]
    # header card
    severity = str(row.get("Overall_Severity", "low")).lower()
    badge_class = "badge-low"
    if severity == "moderate":
        badge_class = "badge-moderate"
    elif severity == "high":
        badge_class = "badge-high"

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <div style="font-size:18px;font-weight:700">
                    {row.get("Patient_Name", "Patient")}
                </div>
                <div style="opacity:0.6">{row.get("Patient_ID","")}</div>
            </div>
            <div class="badge {badge_class}">{severity.capitalize()} Risk</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Findings
    st.markdown("### Synthesized Findings")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(row.get("Findings_Paragraph", "No findings detected."))
    st.markdown('</div>', unsafe_allow_html=True)

    # suspected diseases if present
    suspected = row.get("Suspected_Diseases") or row.get("suspected_diseases") or row.get("Provisional_Diagnosis") or "None identified"
    st.markdown(f"**Identified Conditions:** {suspected}")

    # Recommendations
    st.markdown("### Personalized Recommendations")
    recs = row.get("Recommendations_Structured") or []
    if not recs:
        st.info("No recommendations generated.")
    else:
        for r in recs:
            finding = r.get("finding_text") or r.get("finding") or ""
            rec_text = r.get("recommendation") or r.get("recommendation_text") or ""
            urgency = r.get("urgency", "routine")
            badge_style = "badge-low" if urgency != "urgent" else "badge-high"
            badge_label = "Routine" if urgency != "urgent" else "Urgent"
            st.markdown(f"""
            <div class="rec-card">
                <div style="display:flex;justify-content:space-between">
                    <div>
                        <b>{finding}</b><br/>
                        <div style="opacity:0.75">{rec_text}</div>
                    </div>
                    <div class="badge {badge_style}">{badge_label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Right-aligned Generate PDF
    col1, col2, col3 = st.columns([6, 1, 2])
    with col3:
        gen_clicked = st.button("📄 Generate PDF", key="generate_pdf_btn", use_container_width=True)

    if gen_clicked:
        try:
            pdf_bytes = generate_pdf_bytes_from_row(row)
            if pdf_bytes and len(pdf_bytes) > 0:
                st.session_state["pdf"] = pdf_bytes
                st.success("PDF generated. Use Download button to save.")
            else:
                st.error("PDF generator returned empty bytes.")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

    if st.session_state.get("pdf"):
        col1, col2, col3 = st.columns([6, 1, 2])
        with col3:
            st.download_button("⬇ Download PDF", data=st.session_state["pdf"], file_name="recommendation_report.pdf", mime="application/pdf", use_container_width=True, key="download_pdf_button")

    # ============================================================
    # Local Ollama guarded chat (only shows after report present)
    # ============================================================
    st.divider()
    st.markdown("## 💬 Ask About Your Report (guarded)")

    def is_health_related(question: str) -> bool:
        q = question.lower()
        blocked = ["code", "python", "program", "linux", "windows", "politics", "president", "crypto", "bitcoin", "stock", "movie", "game", "weather"]
        # quick block
        for word in blocked:
            if word in q:
                return False
        allowed_keywords = ["blood", "cholesterol", "ldl", "hdl", "triglycerides", "crp", "infection", "hemoglobin", "platelet", "kidney", "liver", "risk", "diagnosis", "report", "lab", "treatment", "recommendation", "disease", "symptom", "condition", "severity"]
        return any(k in q for k in allowed_keywords)

    def ask_ollama(prompt: str, model: str = "phi3:mini", timeout: int = 60) -> str:
        """
        Calls local Ollama HTTP API. Returns text or an error message.
        """
        try:
            res = requests.post("http://127.0.0.1:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
            if res.status_code == 200:
                body = res.json()
                # Ollama responses vary by version - try common keys
                if "response" in body:
                    return body["response"]
                if "text" in body:
                    return body["text"]
                # fallback: stringify results
                return json.dumps(body)
            else:
                return f"Ollama returned status {res.status_code}"
        except Exception as e:
            return f"Could not contact local Ollama API: {e}"

    # chat input
    user_q = st.text_input("Ask a question related to this report:", key="chat_input")
    colA, colB = st.columns([5, 1])
    with colB:
        ask_clicked = st.button("Ask", key="ask_btn", use_container_width=True)

    if ask_clicked and user_q.strip():
        if not is_health_related(user_q):
            st.warning("I can only answer questions related to the medical report (values, risk, conditions, recommendations).")
        else:
            # build constrained prompt using report context
            prompt = f"""
You are a cautious clinical assistant. STRICT RULES:
- ONLY use the report context below to answer.
- DO NOT answer unrelated questions or provide programming/political/financial content.
- If the question is not about the report, respond with:
  "I can only answer questions related to the provided medical report."

Report findings: {row.get('Findings_Paragraph')}
Overall severity: {row.get('Overall_Severity')}
Identified conditions: {row.get('Suspected_Diseases') or row.get('Provisional_Diagnosis')}

User question: {user_q}

Answer succinctly, avoid speculation, and add a short suggestion to consult a clinician if appropriate.
"""
            with st.spinner("Consulting local assistant..."):
                reply = ask_ollama(prompt)
            # store chat
            st.session_state["chat_history"].append(("user", user_q))
            st.session_state["chat_history"].append(("assistant", reply))

    # render chat history
    if st.session_state["chat_history"]:
        st.markdown("### Conversation")
        for role, text in st.session_state["chat_history"]:
            if role == "user":
                st.markdown(f"<div style='background:#121418;padding:10px;border-radius:8px;margin-bottom:6px;'><b>You:</b><br>{text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#0d1113;padding:10px;border-radius:8px;margin-bottom:6px;'><b>Assistant:</b><br>{text}</div>", unsafe_allow_html=True)
        if st.button("Clear Chat"):
            st.session_state["chat_history"] = []
else:
    st.info("After clicking Run Report you will see a preview here. Then click Generate PDF to create a downloadable file.")

st.caption("This is research-grade automated analysis and does not replace professional medical advice.")

