"""
Multi-Model Orchestrator: run the full pipeline from input to report.
"""
from ingestion.parser import parse_input
from ingestion.extractor import extract_parameters, REQUIRED_NUMERIC
from ingestion.validator import validate_data
from models.model1_interpreter import interpret
from models.model2_ml_risk import calculate_risk
from models.model3_contextual import contextual_adjustment
from synthesis.synthesizer import synthesize
from synthesis.recommender import generate_recommended_actions, generate_synthesis_findings
from report.generator import generate_full_report, build_report_sections

def _detect_format(file) -> str:
    if file is None:
        return "pdf"
    name = (getattr(file, "name", None) or "").lower()
    if name.endswith(".json"):
        return "json"
    if name.endswith(".pdf"):
        return "pdf"
    if name.endswith(".png") or name.endswith(".jpg") or name.endswith(".jpeg"):
        return "png"
    return "pdf"

def run_agent(
    user_input=None,
    file=None,
    age=None,
    gender=None,
    memory=None,
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_model: str = "phi3:mini",
    ollama_timeout_seconds: int = 120,
):
    """
    Main entry point: run the blood report analysis pipeline.
    Uses local Ollama for recommendations (default model: phi3:mini).
    Returns (report_or_message: str, confidence: float, sections: dict|None).
    """
    if file is None:
        return "Please upload a blood report (PDF, PNG, JPG, JPEG, or JSON) for analysis.", 0, None

    fmt = _detect_format(file)
    parsed = parse_input(file, fmt)
    if isinstance(parsed, str) and len(parsed.strip()) < 20:
        return (
            "Could not read enough text from the file. Use a clear, well-lit photo of the report, "
            "or upload a text-based PDF/JSON. Supported parameters include Hemoglobin, Glucose, Cholesterol, WBC, RBC, Platelets.",
            0,
            None,
        )

    raw_data = extract_parameters(parsed)
    extracted = [k for k in REQUIRED_NUMERIC if raw_data.get(k) is not None]
    extracted_count = len(extracted)
    base_conf = 100.0 * extracted_count / len(REQUIRED_NUMERIC)

    data = validate_data(raw_data)
    if not data:
        return (
            "No valid parameters detected in the report. Ensure the file contains blood parameters "
            "(e.g. Hemoglobin, Glucose, Cholesterol, WBC, RBC, Platelets).",
            0,
            None,
        )

    # Confidence adjustments: penalize short OCR text and heavy normalization/clamping
    quality = 1.0
    if isinstance(parsed, str):
        tlen = len(parsed.strip())
    # smoother scaling: short text still allowed but penalized
        quality = max(0.7, min(1.0, tlen / 300.0))


# -------------------------
# 2. CLAMP DETECTION
# -------------------------
    clamped = 0
    for k in extracted:
        try:
            raw_v = raw_data.get(k)
            val_v = data.get(k)

            if raw_v is not None and val_v is not None:
                if abs(float(raw_v) - float(val_v)) > 1e-6:
                    clamped += 1
        except Exception:
            continue


# -------------------------
# 3. NORMALIZED SCORES
# -------------------------
# base_conf is already % (0–100)
    base_score = base_conf / 100.0

# clamp penalty scaled (0–1)
    clamp_ratio = clamped / max(1, len(extracted))
    clamp_score = max(0.0, 1.0 - clamp_ratio)


# -------------------------
# 4. FINAL WEIGHTED SCORE
# -------------------------
    confidence = (
        base_score * 0.5 +      # completeness importance
        quality * 0.3 +         # OCR/text quality
        clamp_score * 0.2       # data reliability
    ) * 100

    confidence = round(max(0.0, min(100.0, confidence)), 1)

    if age is not None:
        data["Age"] = age
    if gender is not None:
        data["Gender"] = gender

    m1 = interpret(data)
    risk = calculate_risk(data, age)
    context_flags = contextual_adjustment(data, age, gender)
    summary = synthesize(m1, risk, context_flags)

    # Enrich summary for LLM-based synthesized findings.
    # Include parameter interpretation statuses and raw values so the model
    # can observe patterns, abnormal parameters, and possible risks.
    summary = dict(summary or {})
    summary["parameter_interpretation"] = m1
    summary["raw_values"] = data

    # Generate synthesized findings via LLM; if the LLM fails or returns nothing,
    # generate_synthesis_findings internally falls back to rule-based key_findings.
    synthesis_findings = generate_synthesis_findings(
        summary,
        base_url=ollama_base_url,
        model=ollama_model,
        timeout_seconds=ollama_timeout_seconds,
    )

    actions = generate_recommended_actions(
        summary,
        base_url=ollama_base_url,
        model=ollama_model,
        age=age,
        gender=gender,
        timeout_seconds=ollama_timeout_seconds,
    )

    parameters = {p: {"value": data[p], "status": m1[p]} for p in m1}
    sections = build_report_sections(parameters, summary, synthesis_findings, actions, confidence)
    report = generate_full_report(parameters, summary, synthesis_findings, actions, confidence)
    return report, confidence, sections
