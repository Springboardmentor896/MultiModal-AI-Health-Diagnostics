"""
Streamlit UI for the Multi-Model AI Health Agent.
Upload blood report (PNG, PDF, JPG, JPEG, JSON) → Submit.
Output: Parameter Interpretation, Analytical Summary, Synthesized Findings,
Recommended Actions, System Confidence, Disclaimer. Then ask questions about the report; download full PDF.
"""
import io
import streamlit as st
from agent.orchestrator import run_agent
from agent.memory import ConversationMemory
from synthesis.recommender import answer_report_query
from utils.ollama import healthcheck, list_models

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()
if "report_sections" not in st.session_state:
    st.session_state.report_sections = None
if "last_report_text" not in st.session_state:
    st.session_state.last_report_text = ""
if "query_answers" not in st.session_state:
    st.session_state.query_answers = []

memory = st.session_state.memory

# Sidebar: Model settings
with st.sidebar:
    st.subheader("Model settings")

    st.caption("Uses local Ollama (default `http://127.0.0.1:11434`).")
    st.session_state.ollama_base_url = st.text_input(
        "Ollama base URL",
        value=st.session_state.get("ollama_base_url", "http://127.0.0.1:11434"),
    )
    st.session_state.ollama_model = st.text_input(
        "Ollama model",
        value=st.session_state.get("ollama_model", "phi3:mini"),
        help="Example: phi3:mini",
    )
    st.session_state.ollama_timeout_seconds = st.number_input(
        "Ollama timeout (seconds)",
        min_value=15,
        max_value=600,
        value=int(st.session_state.get("ollama_timeout_seconds", 120)),
        step=15,
        help="Increase if your model is slow on first response.",
    )
    ok, msg = healthcheck(base_url=st.session_state.ollama_base_url)
    if ok:
        st.success(msg)
        models, err = list_models(base_url=st.session_state.ollama_base_url)
        if err:
            st.info("Connected, but couldn't list models.")
        elif models:
            st.caption("Available models: " + ", ".join(models[:10]) + (" ..." if len(models) > 10 else ""))
    else:
        st.warning(msg)
        st.caption("Start Ollama, then run: `ollama pull phi3:mini` and `ollama run phi3:mini`.")

st.title("Multi-Model AI Health Agent")

# Step 1: Upload report
file = st.file_uploader(
    "Upload Blood Report",
    type=["pdf", "png", "jpg", "jpeg", "json"],
    help="Upload a blood report as PDF, PNG, JPG, JPEG, or JSON (max 200MB).",
)

# Submit button
if st.button("Submit"):
    if file is None:
        st.warning("Please upload a blood report (PNG, PDF, JPG, JPEG, or JSON).")
    else:
        with st.spinner("Processing report..."):
            report_text, confidence, sections = run_agent(
                "Analyze my blood report.",
                file=file,
                age=None,
                gender=None,
                memory=memory,
                ollama_base_url=st.session_state.get("ollama_base_url", "http://127.0.0.1:11434"),
                ollama_model=st.session_state.get("ollama_model", "phi3:mini"),
                ollama_timeout_seconds=int(st.session_state.get("ollama_timeout_seconds", 120)),
            )
        if sections is None:
            st.error(report_text)
        else:
            st.session_state.report_sections = sections
            st.session_state.last_report_text = report_text
            st.session_state.query_answers = []
            st.success("Report analyzed successfully.")

# Show stored sections whenever we have a report (persists across reruns)
if st.session_state.report_sections is not None:
    sections = st.session_state.report_sections

    def build_qa_context(sec: dict) -> str:
        # Keep context small to avoid slow/timeout responses.
        parts = [
            "Parameter Interpretation:",
            (sec.get("parameter_interpretation") or "").strip(),
            "",
            "Analytical Summary:",
            (sec.get("analytical_summary") or "").strip(),
        ]
        ctx = "\n".join(parts).strip()
        return ctx[:3500]

    st.subheader("Parameter Interpretation")
    st.text(sections["parameter_interpretation"])

    st.subheader("Analytical Summary")
    st.text(sections["analytical_summary"])

    st.subheader("Synthesized Findings")
    pr = (sections.get("synthesized_findings") or "").strip()
    if pr:
        st.markdown(pr)
    else:
        st.text("No findings generated.")

    st.subheader("Recommended Actions")
    actions_lines = []
    for line in (sections.get("recommended_actions") or "").splitlines():
        s = line.strip()
        if s.startswith("- "):
            actions_lines.append(s)
        elif s.startswith("• "):
            actions_lines.append("- " + s[2:].strip())
        elif s.startswith("  - "):
            actions_lines.append("- " + s[4:].strip())
    if actions_lines:
        st.markdown("\n".join(actions_lines))
    else:
        st.text(sections.get("recommended_actions") or "")

    st.subheader("System Confidence")
    st.metric("Confidence Score", sections["system_confidence"])

    st.subheader("Disclaimer")
    st.caption(sections["disclaimer"])

    st.divider()
    st.subheader("Ask about your report")
    user_query = st.text_input(
        "Enter your question about the report",
        placeholder="e.g. What should I do about my glucose level?",
        key="report_query",
    )
    if st.button("Get answer", key="answer_btn"):
        if not user_query or not user_query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating answer..."):
                answer = answer_report_query(
                    build_qa_context(st.session_state.report_sections),
                    user_query.strip(),
                    ollama_base_url=st.session_state.get("ollama_base_url", "http://127.0.0.1:11434"),
                    ollama_model=st.session_state.get("ollama_model", "phi3:mini"),
                    timeout_seconds=int(st.session_state.get("ollama_timeout_seconds", 120)),
                )
            if answer:
                st.session_state.query_answers.append((user_query.strip(), answer))
                st.write("**Answer:**")
                st.write(answer)

    # Show previous Q&A
    if st.session_state.query_answers:
        st.subheader("Previous Q&A")
        for q, a in st.session_state.query_answers:
            with st.expander(f"Q: {q[:60]}..." if len(q) > 60 else f"Q: {q}"):
                st.write(a)

    # PDF download
    st.divider()
    st.subheader("Download report")

    def build_pdf_bytes():
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        style_heading = ParagraphStyle(
            name="CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=6,
        )
        story = []
        story.append(Paragraph("AI Health Diagnostic Report", styles["Title"]))
        story.append(Spacer(1, 12))
        for title, key in [
            ("Parameter Interpretation", "parameter_interpretation"),
            ("Analytical Summary", "analytical_summary"),
            ("Synthesized Findings", "synthesized_findings"),
            ("Recommended Actions", "recommended_actions"),
            ("Disclaimer", "disclaimer"),
        ]:
            story.append(Paragraph(title, style_heading))
            text = sections.get(key, "") or ""
            # Use normal wrapped paragraphs for Recommended Actions so lines
            # don't run off the page horizontally.
            if key == "recommended_actions":
                # Preserve line breaks while allowing word-wrapped bullets.
                paragraph_text = "<br/>".join(text.splitlines())
                story.append(Paragraph(paragraph_text, styles["Normal"]))
            else:
                story.append(Preformatted(text, styles["Normal"]))
            story.append(Spacer(1, 8))
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    try:
        pdf_bytes = build_pdf_bytes()
        st.download_button(
            label="Download full report as PDF",
            data=pdf_bytes,
            file_name="health_report.pdf",
            mime="application/pdf",
            key="download_pdf",
        )
    except Exception as e:
        st.error(f"Could not generate PDF: {e}")

st.caption("⚠️ This AI system provides supportive insights only and is not a medical diagnosis tool.")
