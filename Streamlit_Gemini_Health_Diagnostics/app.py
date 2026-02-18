import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
from google import genai
import os
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import io
import re

# ---------------- CONFIG ----------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY not found in .env file")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# ---------------- UI ----------------
st.set_page_config(page_title="AI Health Diagnostics", layout="wide")
st.title("🧠 Multi-Model AI Health Diagnostics")

if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

uploaded_file = st.file_uploader(
    "Upload Blood Report (PDF / PNG / JPG)",
    type=["pdf", "png", "jpg", "jpeg"]
)

# 🔒 Reset chat if new file uploaded
if uploaded_file:
    st.session_state.chat_history = []

# ---------------- TEXT EXTRACTION ----------------

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

# ---------------- ANALYSIS ----------------

def analyze_report(text):
    prompt = f"""
You are a professional medical AI assistant.

Return output STRICTLY in this structured format:

SUMMARY:
<summary text>

RISK_LEVEL:
Low / Moderate / High

STAGE_SEVERITY:
<stage description>

FINAL_HEALTH_STATUS:
Excellent / Stable / Needs Attention / Critical

FINAL_HEALTH_SCORE:
<number between 0-100>

OVERALL_REVIEW:
<holistic interpretation in 1-2 paragraphs>

RECOMMENDATIONS:
<bullet recommendations>

DISCLAIMER:
<medical disclaimer>

CONFIDENCE_SCORE:
<number between 0-100>%

Blood Report:
{text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text

# ---------------- PARSE AI OUTPUT ----------------

def extract_section(text, section_name):
    pattern = rf"{section_name}:\s*(.*?)(?=\n[A-Z_]+:|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else "Not Available"

# ---------------- PDF GENERATOR ----------------

def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Health Diagnostic Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    for line in content.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------- ANALYZE BUTTON ----------------

if uploaded_file:
    if st.button("Analyze Report"):
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_image(uploaded_file)

            st.session_state.report_text = text
            result = analyze_report(text)
            st.session_state.analysis_result = result

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- DISPLAY OUTPUT ----------------

if st.session_state.analysis_result:

    result = st.session_state.analysis_result

    summary = extract_section(result, "SUMMARY")
    risk = extract_section(result, "RISK_LEVEL")
    stage = extract_section(result, "STAGE_SEVERITY")
    final_status = extract_section(result, "FINAL_HEALTH_STATUS")
    health_score = extract_section(result, "FINAL_HEALTH_SCORE")
    overall_review = extract_section(result, "OVERALL_REVIEW")
    recommendations = extract_section(result, "RECOMMENDATIONS")
    disclaimer = extract_section(result, "DISCLAIMER")
    confidence = extract_section(result, "CONFIDENCE_SCORE")

    if "High" in risk:
        st.markdown("### 🔴 High Risk Detected")
    elif "Moderate" in risk:
        st.markdown("### 🟡 Moderate Risk Detected")
    else:
        st.markdown("### 🟢 Low Risk")

    if "Critical" in final_status:
        st.error(f"🏥 Final Health Status: {final_status}")
    elif "Needs Attention" in final_status:
        st.warning(f"🏥 Final Health Status: {final_status}")
    elif "Stable" in final_status:
        st.info(f"🏥 Final Health Status: {final_status}")
    else:
        st.success(f"🏥 Final Health Status: {final_status}")

    try:
        score_value = int(re.search(r'\d+', health_score).group())
    except:
        score_value = 50

    st.subheader("📊 Final Health Score")
    st.progress(score_value / 100)
    st.write(f"Score: {score_value} / 100")

    tabs = st.tabs([
        "📊 Summary",
        "⚠ Risk",
        "🏥 Overall Review",
        "💡 Recommendations",
        "📄 Disclaimer",
        "📈 Confidence"
    ])

    with tabs[0]:
        st.write(summary)

    with tabs[1]:
        st.write(f"Risk Level: {risk}")
        st.write(f"Stage Severity: {stage}")

    with tabs[2]:
        st.write(overall_review)

    with tabs[3]:
        st.write(recommendations)

    with tabs[4]:
        st.write(disclaimer)

    with tabs[5]:
        st.write(f"AI Confidence Score: {confidence}")

    pdf_buffer = generate_pdf(result)
    st.download_button(
        label="📥 Download AI Report",
        data=pdf_buffer,
        file_name="AI_Health_Report.pdf",
        mime="application/pdf"
    )

# ---------------- DOMAIN FILTER ----------------

def is_medical_question(question):
    medical_keywords = [
        "report", "blood", "cbc", "hemoglobin", "platelet",
        "lymphocyte", "mchc", "rbc", "wbc", "health",
        "diagnosis", "risk", "summary", "value",
        "count", "level", "infection", "anemia"
    ]

    question = question.lower()
    return any(word in question for word in medical_keywords)

# ---------------- SMART CHAT SECTION ----------------

st.subheader("💬 Chat About Your Report")
user_question = st.text_input("Ask a question about your report")

if st.button("Send"):

    if st.session_state.report_text == "":
        st.warning("Please analyze a report first.")

    elif user_question.strip() == "":
        st.warning("Please enter a question.")

    elif not is_medical_question(user_question):
        st.session_state.chat_history.append(("User", user_question))
        st.session_state.chat_history.append((
            "AI",
            "I am a medical AI assistant designed only to interpret medical reports. "
            "Please ask questions related to your uploaded health report."
        ))

    else:
        try:
            smart_prompt = f"""
You are a STRICT clinical AI medical assistant.

RULES:
- Answer ONLY questions related to the provided medical report.
- Do NOT answer general knowledge questions.
- Do NOT behave like a general chatbot.
- Stay within medical domain strictly.

Medical Report:
{st.session_state.report_text}

User Question:
{user_question}
"""

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=smart_prompt,
            )

            answer = response.text.strip()

            st.session_state.chat_history.append(("User", user_question))
            st.session_state.chat_history.append(("AI", answer))

        except Exception as e:
            st.error(f"Error: {e}")

# Display Chat History
for role, message in st.session_state.chat_history:
    if role == "User":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 AI:** {message}")
