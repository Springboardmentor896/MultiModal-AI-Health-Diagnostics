"""
Intent Inference Model: rule-based only.
"""

def _rule_based_intent(user_input: str, history: list) -> str:
    """Fallback when LLM is not available."""
    text = (user_input or "").strip().lower()
    if not text:
        return "request_clarification"
    upload_keywords = ("upload", "report", "blood", "analyze", "result", "pdf", "test", "lab")
    if any(k in text for k in upload_keywords) or "?" not in text and len(text) < 100:
        if "report" in text or "upload" in text or "blood" in text or "analyze" in text:
            return "analyze_report"
    if "?" in text or "what" in text or "how" in text or "why" in text or "can " in text:
        return "ask_general_health_question"
    if "report" in text or "upload" in text or "blood" in text:
        return "analyze_report"
    return "ask_general_health_question"

def infer_intent(user_input: str, history: list = None, api_key: str = None) -> str:
    """
    Classify user intent: analyze_report | ask_general_health_question | request_clarification.
    Rule-based only (no external LLM).
    """
    return _rule_based_intent(user_input, history or [])
