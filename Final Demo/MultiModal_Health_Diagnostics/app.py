import streamlit as st
from agent.orchestrator import orchestrator
from report.generator import generate_report, get_recommendations, get_key_findings
import tempfile
import os


# Set page configuration
st.set_page_config(page_title="Multi-Model AI Health Agent", layout="centered")


# Custom CSS to force white theme
st.markdown("""
    <style>
    /* Force white background everywhere */
    .main {
        background-color: #ffffff !important;
    }
    .stApp {
        background-color: #ffffff !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    
    /* Text colors for white background */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #000000 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 1px dashed #ced4da;
        border-radius: 5px;
        padding: 20px;
        background-color: #f8f9fa !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100px;
        background-color: #ffffff !important;
        color: #333 !important;
        border: 1px solid #ced4da !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    
    /* Disclaimer */
    .disclaimer {
        background-color: #fffdf0;
        border: 1px solid #ffeeba;
        padding: 10px;
        border-radius: 5px;
        color: #856404;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'result' not in st.session_state:
    st.session_state.result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


# Title
st.title("Multi-Model AI Health Agent")


# Ask or upload your report
st.write("Ask or upload your report")
query = st.text_input("", placeholder="Type your question or brief description here", label_visibility="collapsed")


# Upload Report Section
st.write("Upload Report")
uploaded_file = st.file_uploader(
    "Drag and drop file here",
    type=["pdf", "png", "jpg", "jpeg", "csv", "txt"],
    help="Limit 200MB per file • PDF/Image/CSV/TXT",
    label_visibility="collapsed"
)


# Age Input
st.write("Age")
age = st.number_input("Age", min_value=1, max_value=120, value=30, step=1, label_visibility="collapsed")


# Gender Select
st.write("Gender")
gender = st.selectbox("Gender", ["Male", "Female"], label_visibility="collapsed")


# Submit Button
if st.button("Submit"):
    if not uploaded_file and not query:
        st.error("Please upload a report file or type a query before submitting.")
    else:
        with st.spinner("🔬 Analyzing your report..."):
            try:
                if uploaded_file:
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    if file_ext == 'pdf':
                        source_type = 'pdf'
                    elif file_ext in ['png', 'jpg', 'jpeg']:
                        source_type = 'image'
                    elif file_ext == 'csv':
                        source_type = 'csv'
                    else:
                        source_type = 'text'

                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    raw_content = tmp_path
                else:
                    raw_content = query
                    source_type = 'text'

                result = orchestrator.orchestrate(
                    raw_content=raw_content,
                    source_type=source_type,
                    age=int(age),
                    gender=gender.lower(),
                    pregnant=False,
                    name="Patient",
                    query=query or "analyze my report"
                )

                if uploaded_file and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

                st.session_state.result = result
                st.session_state.analysis_complete = True

            except Exception as e:
                st.error(f"Error: {str(e)}")


# Display results
if st.session_state.analysis_complete and st.session_state.result:
    result = st.session_state.result

    if result['status'] == 'success':
        st.success("✅ Analysis Complete!")

        analysis = result['analysis']

        # ── SHARED VARIABLES ────────────────────────────────────────────────
        lab_data = analysis.get('lab_data', {})

        # Merge synthesis_summary (overall risk) + risks (per-disease)
        model3_out = {
            **analysis.get('synthesis_summary', {}),
            'risks': analysis.get('risks', {})
        }

        patient_info = {
            'name': 'Patient',
            'age': int(age),
            'gender': gender.lower(),
            'pregnant': False
        }

        # ── TABS ─────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Summary",
            "🩺 Risks",
            "💊 Recommendations",
            "🩺 Clinical Consultation",
            "📄 Full Report"
        ])

        # ── TAB 1: SUMMARY ───────────────────────────────────────────────────
        with tab1:
            st.subheader("Key Findings")

            findings = get_key_findings(lab_data, patient_info)
            if findings:
                for finding in findings[:10]:
                    st.write(f"• {finding}")
            else:
                st.info("No significant abnormal findings detected.")

            col1, col2 = st.columns(2)
            with col1:
                overall_risk = model3_out.get('overall_risk', 'unknown').upper()
                risk_prob    = float(model3_out.get('risk_probability', 0))
                st.metric("Overall Risk", overall_risk, delta=f"{risk_prob:.1f}%")
            with col2:
                conf_level = result['confidence']['level'].upper()
                conf_score = result['confidence']['score']
                st.metric("Confidence", conf_level, delta=f"{conf_score:.1f}/100")

        # ── TAB 2: RISKS ─────────────────────────────────────────────────────
        with tab2:
            st.subheader("Disease Risk Analysis")
            risks = analysis.get('risks', {})
            sorted_risks = sorted(risks.items(), key=lambda x: x[1]['probability'], reverse=True)

            for disease, risk_data in sorted_risks[:8]:
                label = risk_data.get('label', 'unknown')
                prob  = risk_data.get('probability', 0) * 100

                if label == 'high':
                    color = "🔴"
                elif label == 'moderate':
                    color = "🟡"
                else:
                    color = "🟢"

                disease_name = disease.replace('_', ' ').title()
                st.write(f"{color} **{disease_name}**: {prob:.1f}% ({label.upper()})")

                evidence = risk_data.get('evidence', [])
                if evidence:
                    with st.expander("View Evidence"):
                        for ev in evidence:
                            st.write(f"- {ev}")

        # ── TAB 3: RECOMMENDATIONS ───────────────────────────────────────────
        with tab3:
            st.subheader("Personalized Recommendations")

            if st.button("🤖 Generate AI-Powered Recommendations", type="primary", key="gen_ai_recs"):
                with st.spinner("Generating personalized recommendations..."):
                    try:
                        from ai.chat_assistant import HealthChatAssistant
                        assistant = HealthChatAssistant()
                        ai_recs = assistant.generate_clinical_recommendations(
                            lab_data,
                            analysis.get('risks', {}),
                            patient_info
                        )
                        st.markdown(ai_recs)
                        st.success("✅ Recommendations Generated!")
                    except Exception as e:
                        st.error(f"Unable to generate AI recommendations: {str(e)}")
                        st.info("Showing standard recommendations instead:")

            st.markdown("---")
            st.subheader("Standard Clinical Recommendations")

            recommendations = get_recommendations(lab_data, model3_out, patient_info)
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("No specific recommendations at this time.")

        # ── TAB 4: CLINICAL CONSULTATION ─────────────────────────────────────
        with tab4:
            st.subheader("Clinical Consultation")
            st.markdown("""
            <div style='background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0066cc;'>
            <b>💡 Ask questions about your health report</b><br><br>
            <b>Example questions:</b><br>
            • What do my lab results mean?<br>
            • What foods should I eat to improve my values?<br>
            • What lifestyle changes do I need to make?<br>
            • Are these findings concerning?<br>
            • When should I schedule a retest?<br>
            • What supplements should I consider?<br>
            • Which specialist should I consult?
            </div>
            """, unsafe_allow_html=True)

            for msg in st.session_state.chat_history:
                with st.chat_message(msg['role']):
                    st.write(msg['content'])

            if prompt := st.chat_input("Ask about your health..."):
                st.session_state.chat_history.append({'role': 'user', 'content': prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing your question..."):
                        try:
                            from ai.chat_assistant import HealthChatAssistant
                            assistant = HealthChatAssistant()
                            response = assistant.chat_with_report(
                                prompt,
                                lab_data,
                                analysis.get('risks', {}),
                                patient_info,
                                st.session_state.chat_history
                            )
                            st.write(response)
                            st.session_state.chat_history.append(
                                {'role': 'assistant', 'content': response}
                            )
                        except Exception as e:
                            st.error("Unable to respond right now. Please try again later.")

            if st.session_state.chat_history:
                if st.button("🗑️ Start New Consultation", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()

        # ── TAB 5: FULL REPORT ────────────────────────────────────────────────
        with tab5:
            st.subheader("Complete Analysis Report")

            report_text = generate_report(lab_data, patient_info, model3_out)

            st.text_area("Full Report", report_text, height=400, label_visibility="collapsed")
            st.download_button(
                "📥 Download Report (TXT)",
                report_text,
                file_name="health_analysis_report.txt",
                mime="text/plain"
            )

    else:
        st.error(f"Analysis failed: {result.get('message', 'Unknown error')}")
        if result.get('execution_log'):
            with st.expander("View Execution Log"):
                for log in result['execution_log']:
                    st.text(log)


# Disclaimer
st.markdown("""
    <div class="disclaimer">
        ⚠️ This AI system provides supportive health insights based on laboratory values. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions.
    </div>
""", unsafe_allow_html=True)
