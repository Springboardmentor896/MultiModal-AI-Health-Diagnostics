"""
Report Generation Module: format findings and recommendations into the final health report.
"""
from datetime import datetime

DISCLAIMER = """This AI-generated report provides supportive health insights based on the submitted laboratory values.
Please consult a licensed physician for clinical interpretation."""

def _fmt_2dp(v):
    try:
        return f"{float(v):.2f}"
    except (TypeError, ValueError):
        return str(v)

def format_parameter_section(parameters):
    """parameters: dict of param -> {value, status} or param -> str (status only)."""
    lines = []
    for param, details in (parameters or {}).items():
        if isinstance(details, dict):
            val = details.get("value", "")
            status = details.get("status", "")
            lines.append(f"{param}: {_fmt_2dp(val)} ({status})")
        else:
            lines.append(f"{param}: {details}")
    return "\n".join(lines) if lines else "No parameter data available."

def format_summary_section(summary):
    """summary: dict with abnormal_parameters, risk_level, risk_probability, context_notes."""
    lines = []
    s = summary or {}
    abn = s.get("abnormal_parameters") or []
    if abn:
        lines.append("Abnormal Parameters:")
        for p in abn:
            lines.append(f"  - {p}")
    else:
        lines.append("All major parameters are within reference ranges.")
    return "\n".join(lines)


def format_synthesized_findings(findings):
    """
    findings: list of short bullet-point strings (ideal 4–6),
    or a single string as a fallback.
    """
    if not findings:
        return "No synthesized findings generated."

    # Allow backwards compatibility with a single string input
    if isinstance(findings, str):
        text = findings.strip()
        return f"  - {text}" if text else "No synthesized findings generated."

    lines = []
    for idx, item in enumerate(findings):
        if idx >= 6:  # cap at 6 bullet points
            break
        item = (item or "").strip()
        if item:
            lines.append(f"  - {item}")

    return "\n".join(lines) if lines else "No synthesized findings generated."


def format_actions(actions):
    """actions: list of strings."""
    if not actions:
        return "No specific actions generated."
    lines = []
    for idx, a in enumerate(actions):
        if idx >= 6:  # cap at 6 bullet points
            break
        a = (a or "").strip()
        if a:
            lines.append(f"  - {a}")
    return "\n".join(lines) if lines else "No specific actions generated."

def build_report_sections(parameters, summary, synthesis_findings, recommended_actions, confidence):
    """
    Build structured sections dict for display and PDF export.
    Returns dict with: parameter_interpretation, analytical_summary, synthesized_findings,
    recommended_actions, system_confidence, disclaimer.
    """
    return {
        "parameter_interpretation": format_parameter_section(parameters),
        "analytical_summary": format_summary_section(summary),
        "synthesized_findings": format_synthesized_findings(synthesis_findings),
        "recommended_actions": format_actions(recommended_actions),
        "system_confidence": f"{confidence}%",
        "disclaimer": DISCLAIMER,
    }

def generate_full_report(parameters, summary, synthesis_findings, recommended_actions, confidence):
    """
    Build the full AI Health Diagnostic Report string.
    parameters: dict param -> {value, status}
    summary: from synthesis (abnormal_parameters, risk_level, etc.)
    synthesized_findings: list[str] or str
    recommended_actions: list[str] (ideal 4–6 short bullets)
    confidence: number 0–100
    """
    sections = build_report_sections(parameters, summary, synthesis_findings, recommended_actions, confidence)
    report = f"""
=========================
AI HEALTH DIAGNOSTIC REPORT
Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}
=========================

--- Parameter Interpretation ---
{sections['parameter_interpretation']}

--- Analytical Summary ---
{sections['analytical_summary']}

--- Synthesized Findings ---
{sections['synthesized_findings']}

--- Recommended Actions ---
{sections['recommended_actions']}

--- System Confidence ---
Confidence Score: {sections['system_confidence']}

--- Disclaimer ---
{sections['disclaimer']}

=========================
End of Report
=========================
"""
    return report.strip()
