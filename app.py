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
import traceback
import html as _html

# ---------------------------
# Try to import model_engine (preferred). If it fails, create fallbacks so UI still works.
# ---------------------------
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

    # --- Minimal fallback parse / model / pdf functions (keeps UI working) ---
    def parse_parameters(text: str) -> dict:
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
        out["Patient_ID"] = extract_text(["Patient ID", "Patient No", "Patient Number"]) or ""
        out["Patient_Name"] = extract_text(["Patient Name", "Name"]) or "Patient"
        age = extract_numeric(["Age"])
        out["Age"] = int(age) if not np.isnan(age) else np.nan
        out["Gender"] = extract_text(["Gender", "Sex"]) or ""

        out["Hemoglobin_g_dL"] = extract_numeric(["Hemoglobin", r"\bHb\b"])
        out["Triglycerides_mg_dL"] = extract_numeric(["Triglycerides", "TG"])
        out["LDL_mg_dL"] = extract_numeric(["LDL"])
        out["HDL_mg_dL"] = extract_numeric(["HDL"])
        out["CRP_mg_L"] = extract_numeric(["CRP", "C-reactive protein"])
        out["eGFR_mL_min_1_73m2"] = extract_numeric(["eGFR"])
        out["Peripheral_Smear_Result"] = extract_text(["Peripheral Smear Result", "Peripheral Smear"])
        out["Provisional_Diagnosis"] = extract_text(["Provisional Diagnosis", "Diagnosis"])
        return out

    def run_models_on_df(df):
        df = df.copy()
        df["Triglycerides_mg_dL"] = pd.to_numeric(df.get("Triglycerides_mg_dL"), errors="coerce")
        df["LDL_mg_dL"] = pd.to_numeric(df.get("LDL_mg_dL"), errors="coerce")
        df["HDL_mg_dL"] = pd.to_numeric(df.get("HDL_mg_dL"), errors="coerce")

        def cardio_score(r):
            s = 0
            ldl = r.get("LDL_mg_dL")
            hdl = r.get("HDL_mg_dL")
            tg = r.get("Triglycerides_mg_dL")
            if pd.notna(ldl) and ldl > 160:
                s += 3
            elif pd.notna(ldl) and ldl > 130:
                s += 2
            if pd.notna(hdl) and hdl < 40:
                s += 2
            if pd.notna(tg) and tg > 200:
                s += 1
            return s

        df["Cardiovascular_Risk_Score"] = df.apply(cardio_score, axis=1)
        df["Infection_Severity"] = df.get("CRP_mg_L").apply(
            lambda x: "High" if pd.notna(x) and x > 100 else ("Moderate" if pd.notna(x) and x > 10 else "Low")
        ) if "CRP_mg_L" in df else "Low"
        df["Liver_Injury_Flag"] = False
        df["Kidney_Risk_Stage"] = None
        df["Metabolic_Syndrome_Flags"] = 0
        df["TC_HDL_Ratio"] = np.nan
        df["Adjusted_Cardiovascular_Risk"] = df["Cardiovascular_Risk_Score"]
        return df

    def synthesize_and_recommend_df(df):
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

    def generate_pdf_bytes_from_row(row_dict: dict) -> bytes:
        """Fallback PDF builder (ReportLab) which supports LLM recommendations and chat history if present."""
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

        # Findings
        story.append(Paragraph("<b>Synthesized Findings</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(row_dict.get("Findings_Paragraph", "No findings."), styles["BodyText"]))
        story.append(Spacer(1, 12))

        # Overall severity
        story.append(Paragraph(f"<b>Overall Severity:</b> {str(row_dict.get('Overall_Severity','unknown')).capitalize()}", styles["BodyText"]))
        story.append(Spacer(1, 12))

        # Deterministic recommendations
        recs = row_dict.get("Recommendations_Structured", [])
        if recs:
            story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
            story.append(Spacer(1, 6))
            items = []
            for r in recs:
                text = f"<b>Finding:</b> {r.get('finding_text','')}<br/><b>Recommendation:</b> {r.get('recommendation','')}<br/><b>Urgency:</b> {r.get('urgency','routine').capitalize()}"
                items.append(ListItem(Paragraph(text, styles["BodyText"])))
            story.append(ListFlowable(items, bulletType="bullet"))
            story.append(Spacer(1, 12))

        # LLM expanded recommendations (if provided)
        llm_text = row_dict.get("LLM_Expanded_Recommendations")
        if llm_text:
            story.append(Paragraph("<b>LLM Expanded Recommendations</b>", styles["Heading2"]))
            story.append(Spacer(1, 6))
            for chunk in (llm_text if isinstance(llm_text, list) else [llm_text]):
                story.append(Paragraph(str(chunk), styles["BodyText"]))
                story.append(Spacer(1, 6))

        # Chat history
        chat = row_dict.get("Chat_History")
        if chat:
            story.append(Paragraph("<b>Assistant Conversation (chat)</b>", styles["Heading2"]))
            story.append(Spacer(1, 6))
            for role, text in chat:
                entry = f"<b>{role.capitalize()}:</b> {text}"
                story.append(Paragraph(entry, styles["BodyText"]))
                story.append(Spacer(1, 4))

        # Disclaimer
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Disclaimer</b>", styles["Heading3"]))
        story.append(Paragraph("This report is generated by an automated system for research and educational purposes only. It does not replace professional medical advice. Always consult a qualified healthcare provider before making medical decisions.", styles["BodyText"]))

        doc.build(story)
        buf.seek(0)
        return buf.read()

# -------------------------
# page config and session
# -------------------------
st.set_page_config(page_title="AI Health Diagnostics", page_icon="🩺", layout="wide")

# session defaults
if "report_row" not in st.session_state:
    st.session_state["report_row"] = None  # will hold a plain dict when present
if "pdf" not in st.session_state:
    st.session_state["pdf"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # list of tuples (role, text)
if "last_llm_recommendation" not in st.session_state:
    st.session_state["last_llm_recommendation"] = None

# -------------------------
# Styling (dark look)
# -------------------------
st.markdown("""
<style>
.stApp { background: #0b0f12; color:#e6eef2; }
.card {
    background:#0f1316;
    border:1px solid rgba(255,255,255,0.04);
    padding:18px;
    border-radius:12px;
}
.badge { padding:6px 10px; border-radius:999px; font-weight:600; font-size:12px; }
.badge-low { background:#1f2a32; color:#a7d6a6; }
.badge-moderate { background:#2a2320; color:#f4c47a; }
.badge-high { background:#3a1a1d; color:#ff8b94; }
.rec-card { background:#0b0f12; border-radius:10px; padding:14px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.03); }
.small-muted { color:#9aa6b2; font-size:13px; }
.report-box { background:#081016; padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.02); }
.msg-user { background:#08161a; color:#e6eef2; padding:8px; border-radius:10px; display:inline-block; max-width:75%; }
.msg-assistant { background:#0b1220; color:#e6eef2; padding:8px; border-radius:10px; display:inline-block; max-width:75%; }
</style>
""", unsafe_allow_html=True)

# header
st.title("🩺 Multi-Model AI Health Diagnostics")
st.caption("Upload a scanned lab PDF or image")

if IMPORT_ERROR:
    st.warning("Partial import error from model_engine.py. The app will use a fallback analyzer. For full features, fix model_engine.py in the project directory.")
    st.code(IMPORT_ERROR)

st.divider()

# -------------------------
# File upload
# -------------------------
uploaded_file = st.file_uploader("Upload PDF / Image", type=["pdf", "png", "jpg", "jpeg"], key="file_uploader")
if not uploaded_file:
    st.info("Upload a scanned lab PDF or image to begin.")
    st.stop()

file_bytes = uploaded_file.read()
file_name = uploaded_file.name.lower()

# OCR extraction
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

# Provide non-empty label for accessibility
st.markdown("### OCR Output (Editable)")
txt_area_val = st.text_area("OCR output (edit if needed)", extracted_text, height=300, key="ocr_text")

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

                # ensure necessary defaults
                for col in ["Cardiovascular_Risk_Score", "Adjusted_Cardiovascular_Risk", "Metabolic_Syndrome_Flags",
                            "Infection_Severity", "Liver_Injury_Flag", "Kidney_Risk_Stage", "TC_HDL_Ratio"]:
                    if col not in df_single.columns:
                        df_single[col] = "Low" if col == "Infection_Severity" else 0

                df_processed = run_models_on_df(df_single)
                df_m3 = synthesize_and_recommend_df(df_processed)

                # store as plain dict (avoid pandas Series truth ambiguity)
                row0_series = df_m3.iloc[0]
                st.session_state["report_row"] = row0_series.to_dict()
                st.session_state["pdf"] = None
                st.session_state["chat_history"] = []
                st.session_state["last_llm_recommendation"] = None
                st.success("Report ready — preview below.")
            except Exception as e:
                st.error(f"Model processing failed: {e}")
                st.error(traceback.format_exc())
                st.session_state["report_row"] = None

# -------------------------
# Preview and LLM + Chat (if report exists)
# -------------------------
if st.session_state.get("report_row") is not None:
    row = st.session_state["report_row"]

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
                <div style="font-size:18px;font-weight:700">{_html.escape(str(row.get("Patient_Name","Patient")))}</div>
                <div class="small-muted">{_html.escape(str(row.get("Patient_ID","")))}</div>
            </div>
            <div class="badge {badge_class}">{severity.capitalize()} Risk</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Findings
    st.markdown("### Synthesized Findings")
    st.markdown('<div class="report-box">', unsafe_allow_html=True)
    st.write(row.get("Findings_Paragraph", "No findings detected."))
    st.markdown('</div>', unsafe_allow_html=True)

    # Suspected diseases
    suspected = row.get("Suspected_Diseases") or row.get("suspected_diseases") or row.get("Provisional_Diagnosis") or "None identified"
    st.markdown(f"**Identified Conditions:** {_html.escape(str(suspected))}")

    # Deterministic recommendations
    st.markdown("### Personalized Recommendations (engine)")
    recs = row.get("Recommendations_Structured") or []
    if not recs:
        st.info("No deterministic recommendations generated.")
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
                        <b>{_html.escape(str(finding))}</b><br/>
                        <div style="opacity:0.75">{_html.escape(str(rec_text))}</div>
                    </div>
                    <div class="badge {badge_style}">{badge_label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---- LLM-generated recommendations (opt-in button) ----
    st.markdown("### AI (LLM) - Expanded Recommendations")
    colA, colB, colC = st.columns([1, 1, 1])
    with colC:
        run_llm_recs = st.button("Generate LLM Recommendations (local)", key="llm_recs_btn", use_container_width=True)

    # Ollama helper (local only)
    def ask_ollama_raw(prompt: str, model: str = "phi3:mini", timeout: int = 180) -> str:
        try:
            url = "http://127.0.0.1:11434/api/generate"
            payload = {"model": model, "prompt": prompt, "stream": False}
            res = requests.post(url, json=payload, timeout=timeout)
            if res.status_code == 200:
                body = res.json()
                # Best-effort extraction
                if isinstance(body, dict):
                    for k in ("response", "text", "result", "content"):
                        if k in body and isinstance(body[k], str):
                            return body[k]
                    if "choices" in body and isinstance(body["choices"], list) and body["choices"]:
                        ch = body["choices"][0]
                        if isinstance(ch, dict) and "text" in ch:
                            return ch["text"]
                return json.dumps(body)
            else:
                return f"Ollama API returned HTTP {res.status_code}: {res.text}"
        except Exception as e:
            return f"Could not contact local Ollama API: {e}"

    def generate_recommendations_via_ollama(summary: str) -> str:
        prompt = f"""
You are a responsible AI health assistant.

Based on this structured health analysis:

{summary}

Provide:
- General lifestyle suggestions (concise).
- Diet recommendations (concise).
- Exercise advice (concise).

IMPORTANT:
- Do NOT diagnose diseases.
- Do NOT replace medical professionals.
- Use supportive and safe language.
"""
        return ask_ollama_raw(prompt)

    if run_llm_recs:
        # Only call LLM when user explicitly asked
        with st.spinner("Generating LLM recommendations..."):
            try:
                summary = row.get("Findings_Paragraph", "") or "No findings."
                llm_text = generate_recommendations_via_ollama(summary)
                st.session_state["last_llm_recommendation"] = llm_text
                st.success("LLM recommendations generated.")
            except Exception as e:
                st.error(f"LLM generation failed: {e}")
                st.session_state["last_llm_recommendation"] = None

    # show the LLM block if present
    if st.session_state.get("last_llm_recommendation"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**LLM Expanded Recommendations**")
        st.write(st.session_state["last_llm_recommendation"])
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Generate PDF (right aligned)
    col1, col2, col3 = st.columns([6, 1, 2])
    with col3:
        gen_clicked = st.button("📄 Generate PDF", key="generate_pdf_btn", use_container_width=True)

    if gen_clicked:
        try:
            # Merge row dict with LLM text and chat
            merged = dict(row)  # copy
            if st.session_state.get("last_llm_recommendation"):
                merged["LLM_Expanded_Recommendations"] = st.session_state["last_llm_recommendation"]
            if st.session_state.get("chat_history"):
                merged["Chat_History"] = st.session_state["chat_history"]

            # call generator (fallback or model_engine's)
            pdf_bytes = generate_pdf_bytes_from_row(merged)
            if pdf_bytes and len(pdf_bytes) > 0:
                st.session_state["pdf"] = pdf_bytes
                st.success("PDF generated. Use the Download button to save.")
            else:
                st.error("PDF generation returned empty bytes.")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")
            st.error(traceback.format_exc())

    if st.session_state.get("pdf"):
        col1, col2, col3 = st.columns([6, 1, 2])
        with col3:
            st.download_button("⬇ Download PDF", data=st.session_state["pdf"], file_name="recommendation_report.pdf", mime="application/pdf", use_container_width=True, key="download_pdf_button")

    # ============================================================
    # Guarded LLM Chat section (shows after the LLM recommendation block)
    # ============================================================
    st.divider()
    st.markdown("## 💬 Ask About Your Report (guarded)")

    # Health-related quick filter:
    def is_health_related(question: str) -> bool:
        q = question.lower()
        blocked = ["code", "python", "program", "linux", "windows", "politics", "president", "crypto", "bitcoin", "stock", "movie", "game", "weather"]
        for word in blocked:
            if word in q:
                return False
        allowed_keywords = ["blood", "cholesterol", "ldl", "hdl", "triglycerides", "crp", "infection", "hemoglobin", "platelet", "kidney", "liver", "risk", "diagnosis", "report", "lab", "treatment", "recommendation", "disease", "symptom", "condition", "severity"]
        return any(k in q for k in allowed_keywords)

    def generate_general_health_response(user_input: str) -> str:
        prompt = f"""
Answer this health-related question in an informational way.
Do not diagnose. Encourage consulting a doctor if needed.

Question:
{user_input}
"""
        return ask_ollama_raw(prompt)

    # Display previous conversation above input (like a messaging app)
    if st.session_state.get("chat_history"):
        st.markdown("### Conversation")
        for role, text in st.session_state["chat_history"]:
            safe_text = _html.escape(str(text)).replace("\n", "<br/>")
            if role == "user":
                st.markdown(f"<div style='text-align:right;padding:8px;'><b>You:</b><div class='msg-user'>{safe_text}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:left;padding:8px;'><b>Assistant:</b><div class='msg-assistant'>{safe_text}</div></div>", unsafe_allow_html=True)
        if st.button("Clear Chat", key="clear_chat_btn"):
            st.session_state["chat_history"] = []
            st.session_state["last_llm_recommendation"] = None

    # Chat input
    user_q = st.text_input("Ask a question related to this report:", key="chat_input")
    colA, colB = st.columns([5, 1])
    with colB:
        ask_clicked = st.button("Ask", key="ask_btn", use_container_width=True)

    if ask_clicked and user_q and user_q.strip():
        if not is_health_related(user_q):
            st.warning("I can only answer questions related to the medical report (values, risk, conditions, recommendations).")
        else:
            # use constrained prompt and only call LLM if Ollama present
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
                reply = ask_ollama_raw(prompt)
            st.session_state["chat_history"].append(("user", user_q))
            st.session_state["chat_history"].append(("assistant", reply))
            st.success("Assistant responded — see Conversation above.")

else:
    st.info("After clicking Run Report you will see a preview here. Then click Generate PDF to create a downloadable file.")

st.caption("This is research-grade automated analysis and does not replace professional medical advice.")

