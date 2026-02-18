Multi-Model AI Health Diagnostic Agent
HealthAI is a modular, privacy-focused AI platform designed to parse complex medical reports and provide human-readable clinical insights. It leverages a local-first LLM approach to ensure 100% data confidentiality.

🌟 Key Features
Automated Data Extraction: Converts non-searchable PDF lab reports into structured data using Regex and RAG.
Privacy-First Architecture: Utilizes a local Ollama instance (TinyDolphin) to process sensitive health data on-device.
Smart Interpretations: Translates raw numeric lab values (e.g., Hemoglobin, Cholestrol) into clear, status-based insights.
Interactive Dashboard: Built with Streamlit, featuring real-time analysis, confidence scoring, and downloadable TXT reports.

🏗️ Project Structure
├── agent/            # Orchestrator,Intent Inference, Planner, and Memory logic
├── ingestion/        # Data extraction, parsing, and validation
├── models/           # Parameter interpretation, risk score and contextual analysis logic
├── rag/              # Knowledge base for medical guidelines
├── synthesis/        # Clinical interpretation,recommendation and confidence engine
├── report/           # Final report generation logic
├── utils/            # Shared reference range lookups
└── app.py            # Streamlit UI Entry point
