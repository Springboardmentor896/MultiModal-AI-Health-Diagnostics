import streamlit as st
import os
import tempfile
from PIL import Image
from models.main_orchestrator import MedicalAgentOrchestrator

st.set_page_config(page_title="Hybrid AI Health Agent", layout="wide", page_icon="🧬")

with st.sidebar:
    st.header("Settings")
    
    api_key = st.text_input("Google Gemini API Key", type="password")
    ollama_model = st.selectbox("Local Model", ["llama3", "mistral", "phi3"], index=0)
    
    st.divider()
    
    if api_key:
        if 'agent' not in st.session_state:
            try:
                st.session_state.agent = MedicalAgentOrchestrator(
                    api_key=api_key,
                    ollama_model=ollama_model
                )
                st.success("System Online")
            except Exception as e:
                st.error(f"Init Error: {e}")
    else:
        st.warning("Enter Gemini API Key to start.")
        st.stop()

st.title("AI Health Agent (Efficiency Mode)")
st.caption("Gemini 2.5 Flash (Cached) | Local Ollama (Free)")

uploaded_file = st.file_uploader("Upload Blood Report", type=["png", "jpg", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(uploaded_file, caption="Report Preview", use_container_width=True)

    with col2:
        if st.button("Analyze Report", type="primary"):
            with st.spinner("Processing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                # Run Pipeline
                res = st.session_state.agent.run_pipeline(tmp_path)
                st.session_state.results = res # Save results to session
                os.remove(tmp_path)

    if 'results' in st.session_state and st.session_state.results['success']:
        res = st.session_state.results
        
        st.divider()
        st.subheader(f"Patient: {res['profile']['name']}")
        
        st.markdown("### Clinical Summary")
        st.info(res['report'])
        
        # 2. Recommendations (Gemini - Cached)
        st.markdown("### Personalized Advice")
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.markdown("**Diet**")
            for x in res['recommendations'].get('diet', []): st.write(f"- {x}")
        with c2: 
            st.markdown("**Lifestyle**")
            for x in res['recommendations'].get('lifestyle', []): st.write(f"- {x}")
        with c3: 
            st.markdown("**Medical**")
            for x in res['recommendations'].get('medical', []): st.write(f"- {x}")

        # 3. Chat (Local Ollama)
        st.divider()
        st.subheader("Chat with Agent")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about your report..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
