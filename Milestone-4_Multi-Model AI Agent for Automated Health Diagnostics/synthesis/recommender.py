"""
Personalized Recommendation Generator: local Ollama LLM (fallback: rule-based).
"""
from utils.ollama import chat, list_models

def _rule_based_recommendations(summary, age=None, gender=None):
    recs = []
    handled = set()
    findings = summary.get("key_findings") or []
    for finding in findings:
        f = finding.lower()
        if ("anemia" in f or "hemoglobin" in f) and "anemia" not in handled:
            recs.append(
                "Increase iron-rich foods like spinach and dates; consider ferritin test if fatigue persists."
            )
            handled.add("anemia")
        if ("wbc" in f or "infection" in f or "oxygen transport" in f) and "immunity" not in handled:
            recs.append(
                "Ensure adequate hydration, rest, and consult a doctor if fever or weakness continues."
            )
            handled.add("immunity")
        if ("cholesterol" in f or "cardio" in f) and "cardio" not in handled:
            recs.append(
                "Adopt a low-fat diet, include brisk walking, and consult a physician for lipid control."
            )
            handled.add("cardio")
        if ("glucose" in f or "diabetes" in f) and "diabetes" not in handled:
            recs.append(
                "Reduce intake of sugary foods, perform daily exercise, and consider HbA1c testing."
            )
            handled.add("diabetes")
        if ("platelet" in f or "bleeding" in f) and "bleeding" not in handled:
            recs.append(
                "Avoid injury-prone activities and consult a doctor for platelet evaluation."
            )
            handled.add("bleeding")
    a = age if age is not None else 35
    g = (gender or "").strip().lower()
    if a > 55:
        recs.append("Schedule regular full body checkups every 6 months.")
    if g == "male":
        recs.append("Maintain heart health with regular cardio exercise.")
    if not recs:
        recs.append("Stay hydrated, maintain a balanced diet and regular physical activity.")
    return recs

def generate_synthesis_findings(
    summary: dict,
    base_url: str = "http://127.0.0.1:11434",
    model: str = "phi3:mini",
    timeout_seconds: int = 90,
) -> list[str]:
    """
    Generate short, patient-friendly findings (max 6 points, NOT recommendations).
    """

    system = (
        "You are a responsible AI health assistant.\n"
        "Summarize findings from a blood report.\n\n"
        "STRICT RULES:\n"
        "- Do NOT give recommendations.\n"
        "- Do NOT suggest actions.\n"
        "- Do NOT diagnose diseases.\n"
        "- Use neutral, observational language.\n"
        "- Use simple, layman terms that any adult can understand.\n"
        "- Each bullet must be ONE short sentence (aim for under 20 words).\n"
        "- Avoid medical jargon, abbreviations, and numerical probabilities where possible.\n"
        "- Return MAX 6 bullet points ONLY.\n"
        "- Each must start with '- '.\n"
    )

    user = (
        "Generate up to 6 key findings from the report.\n"
        "Only describe what the values indicate, using simple language that a non-medical person can understand.\n\n"
        f"Analysis summary: {summary}\n"
    )

    text, err = chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        model=model,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )

    if text and not err:
        lines = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("- "):
                item = s[2:].strip()
                if item:
                    lines.append(item)

        if lines:
            return lines[:6]

    # fallback
    findings = []

    for f in summary.get("key_findings", []):
        f_lower = f.lower()

        if "hemoglobin" in f_lower:
            findings.append(
                "Hemoglobin is outside the usual healthy range, which may slightly reduce how well blood carries oxygen."
            )

        elif "glucose" in f_lower:
            findings.append(
                "Blood sugar (glucose) is higher than the usual healthy range."
            )

        elif "platelet" in f_lower:
            findings.append(
                "Platelet count is within the usual healthy range."
            )

        elif "wbc" in f_lower:
            findings.append(
                "White blood cell count is not in the usual healthy range, which can relate to your body’s immunity."
            )

        else:
            findings.append(f"Observation from your report: {f}")

    if not findings:
        findings.append("No significant variations detected in the summary.")

    return findings[:6]


def generate_recommended_actions(
    summary: dict,
    base_url: str = "http://127.0.0.1:11434",
    model: str = "phi3:mini",
    age: int | None = None,
    gender: str | None = None,
    timeout_seconds: int = 90,
) -> list[str]:
    """
    Generate a bullet list of actionable steps (up to 6 items).
    Uses Ollama; falls back to rule-based actions.
    """
    system = (
        "You are a responsible AI health assistant. Do NOT diagnose. "
        "Return ONLY bullet points that start with '- '. No extra text.\n"
        "Use short, simple sentences that are easy for any patient to understand."
    )
    user = (
        "From the structured analysis, produce up to 6 practical actions (diet, activity, follow-up tests, when to see a doctor). "
        "Write each action as one short, clear sentence in simple language.\n"
        "Return ONLY bullet points starting with '- '.\n\n"
        f"Analysis summary: {summary}\n"
    )
    text, err = chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        model=model,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )
    if text and not err:
        lines = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("- "):
                item = s[2:].strip()
                if item:
                    lines.append(item)
        if lines:
            return lines[:6]
    return _rule_based_recommendations(summary, age=age, gender=gender)


def answer_report_query(
    report_text: str,
    user_query: str,
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_model: str = "phi3:mini",
    timeout_seconds: int = 120,
) -> str:
    """
    Answer a user question about their blood report.
    Uses report context only.
    """
    if not (report_text or "").strip():
        return "No report context available. Please upload and analyze a report first."

    # Hard guardrail: very short or clearly unrelated questions
    # should not be answered. Return the fixed refusal message.
    q = (user_query or "").strip()
    q_lower = q.lower()
    if not q:
        return "I can only answer questions related to your uploaded health report."

    health_keywords = [
        "blood",
        "report",
        "hemoglobin",
        "glucose",
        "cholesterol",
        "wbc",
        "rbc",
        "platelet",
        "lab",
        "test",
        "result",
        "values",
        "health",
    ]
    if len(q) < 5 or not any(k in q_lower for k in health_keywords):
        return "I can only answer questions related to your uploaded health report."

    system = """
You are a responsible AI health assistant.

STRICT RULES:
1. You must answer ONLY if the question is directly related to the provided blood report.
2. If the question is unrelated (general knowledge, coding, weather, etc.), respond EXACTLY with:
   "I can only answer questions related to your uploaded health report."
3. Do NOT use outside knowledge.
4. Do NOT guess or hallucinate.
5. Do NOT diagnose diseases.
6. Keep answers simple and supportive.
7. Keep answers very brief: 2 or 3 short sentences ONLY.
8. Use plain, easy-to-understand language. Avoid medical jargon.

Before answering:
- First decide if the question is related to the report.
- If NOT related, return the refusal message ONLY.
"""
    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"--- Blood Report ---\n{report_text}\n\n--- User Question ---\n{user_query}\n",
        },
    ]
    text, err = chat(messages=messages, model=ollama_model, base_url=ollama_base_url, timeout_seconds=timeout_seconds)
    if text and not err:
        return text

    # If the request timed out, retry once with truncated context (smaller prompt = faster)
    if (err or "").lower().find("timed out") != -1 or (err or "").lower().find("timeout") != -1:
        short_report = (report_text or "").strip()
        if len(short_report) > 2000:
            short_report = short_report[:2000] + "\n...[truncated]..."
        retry_msgs = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"--- Blood Report (short) ---\n{short_report}\n\n--- User Question ---\n{user_query}\n"},
        ]
        text2, err2 = chat(messages=retry_msgs, model=ollama_model, base_url=ollama_base_url, timeout_seconds=timeout_seconds)
        if text2 and not err2:
            return text2
        err = err2 or err

    models, models_err = list_models(base_url=ollama_base_url)
    if models_err:
        return (
            "Unable to reach Ollama or generate a response.\n\n"
            f"Check that Ollama is running and reachable at `{ollama_base_url}`.\n"
            "If you haven't started it yet, run `ollama serve` (or just open the Ollama app).\n"
            f"Error: {err or models_err}"
        )
    if ollama_model not in models:
        return (
            "Ollama is reachable, but the selected model is not available.\n\n"
            f"Missing model: `{ollama_model}`\n"
            f"Available models: {', '.join(models) if models else '(none)'}\n"
            f"Run: `ollama pull {ollama_model}` then `ollama run {ollama_model}`."
        )
    return (
        "Unable to generate a response from Ollama.\n\n"
        f"Server: `{ollama_base_url}`\nModel: `{ollama_model}`\n"
        f"Error: {err or 'Unknown error'}"
    )
