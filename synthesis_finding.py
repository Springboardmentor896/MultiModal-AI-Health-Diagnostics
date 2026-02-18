
import os
import subprocess
import re
import json
import warnings
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional

warnings.filterwarnings("ignore")

def _call_ollama(prompt: str, model: str = "tinyllama") -> str:
    """Call ollama with a prompt and return the response."""
    try:
        result = subprocess.run([
            "ollama", "run", model, prompt
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Ollama error: {result.stderr}")
            return ""
    except Exception as e:
        print(f"Ollama call failed: {e}")
        return ""

# ── Data class kept for backward compat ─────────────────────────────
@dataclass(frozen=True)
class Finding:
    finding_id: str
    title: str
    details: str
    severity: str
    source: str
    parameter: Optional[str] = None
    value: Optional[float] = None
    status: Optional[str] = None


# ── Helper utilities ────────────────────────────────────────────────
def _severity_from_status(status: str) -> str:
    s = (status or "").upper()
    if s == "HIGH":
        return "high"
    if s == "LOW":
        return "moderate"
    return "low"


def _severity_from_risk_text(text: str) -> str:
    t = text.upper()
    if "CRITICAL" in t:
        return "critical"
    if "HIGH" in t:
        return "high"
    if "MODERATE" in t:
        return "moderate"
    return "low"


def _fid(counter: int) -> str:
    return f"F{counter:03d}"


# ── Build structured findings (rule-based, fast) ────────────────────
def _build_structured_findings(
    model1_classification: Dict[str, Dict[str, Any]],
    model2_risk_assessment: Dict[str, Any],
    model2_patterns: Optional[Iterable[str]] = None,
) -> List[Finding]:
    """Create Finding objects from model outputs (deterministic)."""
    findings: List[Finding] = []
    counter = 1

    for param, info in model1_classification.items():
        status = str(info.get("status", "Normal"))
        if status == "Normal":
            continue
        value = info.get("value")
        findings.append(Finding(
            finding_id=_fid(counter),
            title=f"{status} {param}",
            details=f"{param} is {status.lower()} at {value}.",
            severity=_severity_from_status(status),
            source="model1",
            parameter=param,
            value=value,
            status=status,
        ))
        counter += 1

    risk_level = model2_risk_assessment.get("risk_level", "UNKNOWN")
    risk_score = model2_risk_assessment.get("risk_score")
    risks = model2_risk_assessment.get("identified_risks", []) or []

    if risk_level and risk_level != "UNKNOWN":
        findings.append(Finding(
            finding_id=_fid(counter),
            title=f"Overall risk level: {risk_level}",
            details=f"Risk score {risk_score} with level {risk_level}.",
            severity=_severity_from_risk_text(risk_level),
            source="model2",
        ))
        counter += 1

    for risk_text in risks:
        findings.append(Finding(
            finding_id=_fid(counter),
            title="Risk indicator",
            details=str(risk_text),
            severity=_severity_from_risk_text(str(risk_text)),
            source="model2",
        ))
        counter += 1

    if model2_patterns:
        for pattern in model2_patterns:
            findings.append(Finding(
                finding_id=_fid(counter),
                title="Pattern detected",
                details=str(pattern),
                severity=_severity_from_risk_text(str(pattern)),
                source="model2",
            ))
            counter += 1

    return findings


# ── LLM summary generation using Ollama ────────────────────────────
def _generate_llm_summary(findings: List[Finding],
                          risk_level: str,
                          risk_score: Optional[int],
                          user_context: Optional[Dict[str, Any]]) -> str:
    """Call Ollama TinyLlama to produce a coherent clinical summary."""
    
    try:
        # Build simple prompt for synthesis
        abnormal_lines = []
        for f in findings:
            if f.source == "model1" and f.parameter and f.status != "Normal":
                abnormal_lines.append(f"{f.parameter}: {f.value} ({f.status})")
        
        risks = [f.details for f in findings
                 if f.title in {"Risk indicator", "Pattern detected"}]
        
        patient_info = ""
        if user_context:
            parts = []
            if user_context.get("age"):
                parts.append(f"Age: {user_context['age']}")
            if user_context.get("gender"):
                parts.append(f"Gender: {user_context['gender']}")
            if parts:
                patient_info = ", ".join(parts)
        
        prompt = f"""You are a medical AI. Write a 3-sentence clinical summary.

Patient: {patient_info}
Risk Level: {risk_level} (score {risk_score})

Abnormal Parameters:
{chr(10).join(abnormal_lines[:6])}

Key Risks:
{chr(10).join(f"- {risk}" for risk in risks[:4])}

Write a concise clinical summary (3 sentences max):"""
        
        print("[synthesis_finding] Generating summary with Ollama...")
        summary = _call_ollama(prompt)
        
        if summary and len(summary) > 20:
            return summary
        else:
            # Fallback if ollama fails
            print("[synthesis_finding] Ollama output insufficient, using fallback")
            return _fallback_summary(findings, risk_level, risk_score)
        
    except Exception as e:
        print(f"[synthesis_finding] Ollama generation error: {e}")
        return _fallback_summary(findings, risk_level, risk_score)


def _fallback_summary(findings: List[Finding],
                      risk_level: str,
                      risk_score: Optional[int]) -> str:
    """Rule-based fallback if LLM produces empty output."""
    abnormal = [
        f"{f.parameter} {f.status.lower()} ({f.value})"
        for f in findings if f.source == "model1" and f.parameter and f.status
    ]
    risks = [f.details for f in findings
             if f.title in {"Risk indicator", "Pattern detected"}]

    parts = []
    if risk_level and risk_level != "UNKNOWN":
        parts.append(f"Overall risk {risk_level} (score {risk_score}).")
    if abnormal:
        parts.append("Abnormal parameters: " + ", ".join(abnormal) + ".")
    if risks:
        parts.append("Key risks: " + "; ".join(risks[:3]) + ".")
    return " ".join(parts) or "No significant findings detected."


# ── Public API (same signature as before) ───────────────────────────
def synthesize_findings(
    model1_classification: Dict[str, Dict[str, Any]],
    model2_risk_assessment: Dict[str, Any],
    model2_patterns: Optional[Iterable[str]] = None,
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Synthesise classification + risk data and produce an LLM-generated
    clinical summary using TinyLlama-1.1B-Chat.

    Returns the same dict structure as before so downstream code is
    unchanged.
    """

    # 1. Build structured findings (deterministic)
    findings = _build_structured_findings(
        model1_classification, model2_risk_assessment, model2_patterns
    )

    risk_level = model2_risk_assessment.get("risk_level", "UNKNOWN")
    risk_score = model2_risk_assessment.get("risk_score")

    # 2. Generate LLM summary
    summary = _generate_llm_summary(findings, risk_level, risk_score, user_context)

    # 3. Demographic context
    demographic_context = {}
    if user_context:
        demographic_context = {
            "age": user_context.get("age"),
            "gender": user_context.get("gender"),
            "history": user_context.get("history"),
        }

    return {
        "summary": summary,
        "findings": [asdict(f) for f in findings],
        "risk_level": risk_level,
        "risk_score": risk_score,
        "demographic_context": demographic_context,
    }
