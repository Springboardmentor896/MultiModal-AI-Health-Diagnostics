import streamlit as st
from agent.orchestrator import run_agent
from agent.memory import ConversationMemory
from datetime import datetime

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

st.set_page_config(page_title="Health AI Agent", page_icon="🏥")

st.title("Multi-Model AI Health Agent")

user_input = st.text_input("Ask a health question or upload a report below:")

file = st.file_uploader("Upload Blood Report", type=["pdf"])

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
with col2:
    gender = st.selectbox("Gender", ["Male", "Female","Others"])

if st.button("Submit"):
    with st.spinner("Analyzing clinical data..."):
        report, confidence = run_agent(
            user_input=user_input, 
            file=file, 
            age=age, 
            gender=gender, 
            memory=st.session_state.memory
        )
        st.subheader("Generated Report")
        st.text_area(label="", value=report, height=500)
        st.write(f"**Confidence Score:** {confidence}%")
        st.download_button(
            label="📥 Download Report (TXT)",
            data=report,
            file_name=f"Health_Analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

st.divider()
st.warning("This AI system provides supportive insights only and is not a medical diagnosis tool.")
