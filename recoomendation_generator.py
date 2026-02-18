
import os
import subprocess
import re
import warnings
from typing import Any, Dict, Iterable, List, Optional, Tuple

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


# ── Parse LLM output into structured recommendations ────────────────
def _parse_llm_recommendations(
    text: str, findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Extract structured recommendations from free-text LLM output."""
    recommendations = []
    counter = 1

    # Map keywords → category
    category_map = {
        "diet": "diet",
        "lifestyle": "lifestyle",
        "follow_up": "follow_up",
        "follow-up": "follow_up",
        "followup": "follow_up",
        "precaution": "precautions",
        "precautions": "precautions",
        "exercise": "lifestyle",
    }

    # Find related finding IDs based on parameter mentions
    def _related_ids(text_line: str) -> List[str]:
        ids = []
        t = text_line.lower()
        for f in findings:
            param = (f.get("parameter") or "").lower()
            if param and param in t:
                ids.append(f.get("finding_id", ""))
        return ids

    # Try bracket-tagged parsing first:  [DIET] some text ...
    bracket_pattern = re.compile(
        r"\[(\w[\w\-_]*)\]\s*(.+)", re.IGNORECASE
    )

    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip().lstrip("•-0123456789.) ")
        if not line:
            continue
        m = bracket_pattern.match(line)
        if m:
            raw_cat = m.group(1).lower().replace("-", "_")
            cat = category_map.get(raw_cat, raw_cat)
            rec_text = m.group(2).strip()
        else:
            # Heuristic: detect category from keywords at start
            lower = line.lower()
            cat = "general"
            for kw, c in category_map.items():
                if lower.startswith(kw):
                    cat = c
                    rec_text = line[len(kw):].lstrip(":- ").strip()
                    break
            else:
                rec_text = line

        if len(rec_text) < 10:
            continue  # skip garbage lines

        recommendations.append({
            "recommendation_id": f"R{counter:03d}",
            "category": cat,
            "text": rec_text,
            "related_findings": _related_ids(rec_text),
        })
        counter += 1

    return recommendations


# ── Rule-based fallback ─────────────────────────────────────────────
def _fallback_recommendations(
    findings: List[Dict[str, Any]], risk_level: str,
    user_context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Deterministic recommendations if LLM produces unusable output."""
    recs: List[Dict[str, Any]] = []
    counter = 1

    keyword_recs = {
        "glucose": [
            ("diet", "Reduce added sugars and refined carbs; choose oats, brown rice, legumes."),
            ("lifestyle", "Aim for at least 150 minutes/week of moderate exercise."),
            ("follow_up", "Recheck fasting glucose or HbA1c as advised."),
        ],
        "cholesterol": [
            ("diet", "Favor unsaturated fats (olive oil, nuts) and add soluble fiber."),
            ("lifestyle", "Add aerobic activity to improve lipid profile."),
            ("follow_up", "Schedule a lipid panel review with your clinician."),
        ],
        "hemoglobin": [
            ("diet", "Include iron-rich foods (lentils, spinach, lean meats) with vitamin C."),
            ("follow_up", "Ask about iron studies or CBC follow-up testing."),
        ],
        "wbc": [
            ("lifestyle", "Monitor for fever or infection symptoms."),
            ("follow_up", "Repeat CBC if symptoms persist."),
        ],
        "creatinine": [
            ("diet", "Stay hydrated; moderate sodium and protein intake."),
            ("follow_up", "Discuss kidney function testing with your doctor."),
        ],
        "ast": [
            ("diet", "Limit alcohol; prioritize whole foods."),
            ("follow_up", "Consider a repeat liver panel."),
        ],
        "alt": [
            ("diet", "Limit alcohol; avoid excess fried or processed foods."),
            ("follow_up", "Consider a repeat liver panel."),
        ],
        "platelet": [
            ("lifestyle", "Avoid activities with high bleeding risk."),
            ("follow_up", "Discuss platelet trends with a clinician."),
        ],
    }

    for f in findings:
        combined = f"{f.get('title', '')} {f.get('details', '')}".lower()
        for kw, rec_list in keyword_recs.items():
            if kw in combined:
                for cat, txt in rec_list:
                    recs.append({
                        "recommendation_id": f"R{counter:03d}",
                        "category": cat,
                        "text": txt,
                        "related_findings": [f.get("finding_id", "")],
                    })
                    counter += 1

    if risk_level in ("CRITICAL", "HIGH"):
        recs.append({
            "recommendation_id": f"R{counter:03d}",
            "category": "follow_up",
            "text": "Arrange a clinical review promptly due to elevated risk level.",
            "related_findings": [],
        })
        counter += 1

    # De-duplicate
    seen = set()
    deduped = []
    for r in recs:
        key = (r["category"], r["text"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


# ── Dedupe helper ───────────────────────────────────────────────────
def _dedupe(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in recommendations:
        key = (r.get("category"), r.get("text"))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


# ── Public API ──────────────────────────────────────────────────────
def generate_recommendations(
    synthesized_report: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate health recommendations using Ollama TinyLlama.

    Parameters
    ----------
    synthesized_report : dict
        Output of ``synthesize_findings()``.
    user_context : dict, optional
        Keys: age, gender, history, activity_level.

    Returns
    -------
    dict  with ``recommendations`` list and ``linking_strategy``.
    """
    findings = synthesized_report.get("findings", []) or []
    risk_level = (synthesized_report.get("risk_level") or "").upper()
    summary = synthesized_report.get("summary", "")

    # --- Ollama LLM generation ---
    try:
        # Build simple prompt for recommendations
        patient_info = ""
        if user_context:
            parts = []
            if user_context.get("age"):
                parts.append(f"Age: {user_context['age']}")
            if user_context.get("gender"):
                parts.append(f"Gender: {user_context['gender']}")
            if user_context.get("activity_level"):
                parts.append(f"Activity: {user_context['activity_level']}")
            if parts:
                patient_info = ", ".join(parts)

        # Collect abnormal parameters
        abnormal_params = []
        for f in findings:
            if f.get("source") == "model1" and f.get("parameter"):
                abnormal_params.append(f"{f['parameter']} {f.get('status', '')}")

        prompt = f"""You are a responsible AI health assistant. Give 6 specific recommendations.

Patient: {patient_info}
Risk Level: {risk_level}
Summary: {summary}
Abnormal Parameters: {', '.join(abnormal_params)}

Provide 6 health recommendations. Start each with [DIET], [LIFESTYLE], [FOLLOW_UP], or [PRECAUTIONS]:

[DIET] 
[LIFESTYLE] 
[FOLLOW_UP] 
[PRECAUTIONS] 
[DIET] 
[LIFESTYLE] """

        print("[recommendation_generator] Generating recommendations with Ollama...")
        response = _call_ollama(prompt)
        
        # Parse recommendations
        recommendations = []
        counter = 1
        
        category_map = {
            "diet": "diet",
            "lifestyle": "lifestyle", 
            "follow_up": "follow_up",
            "follow-up": "follow_up",
            "precautions": "precautions"
        }
        
        if response:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('[') and ']' in line:
                    bracket_end = line.find(']')
                    if bracket_end > 0:
                        cat_raw = line[1:bracket_end].lower()
                        text = line[bracket_end+1:].strip()
                        
                        if len(text) > 10:  # Valid recommendation
                            cat = category_map.get(cat_raw, cat_raw)
                            recommendations.append({
                                "recommendation_id": f"R{counter:03d}",
                                "category": cat,
                                "text": text,
                                "related_findings": []
                            })
                            counter += 1
        
        # Fallback recommendations if parsing failed
        if len(recommendations) < 3:
            print("[recommendation_generator] Ollama output insufficient, using fallback")
            recommendations = _fallback_recommendations(findings, risk_level, user_context)

    except Exception as e:
        print(f"[recommendation_generator] Ollama error: {e} — using fallback")
        recommendations = _fallback_recommendations(
            findings, risk_level, user_context
        )

    # Add urgent follow-up for critical risk
    if risk_level in ("CRITICAL", "HIGH"):
        urgent = {
            "recommendation_id": f"R{len(recommendations)+1:03d}",
            "category": "follow_up",
            "text": "Arrange a clinical review promptly due to elevated risk level.",
            "related_findings": [],
        }
        recommendations.append(urgent)

    return {
        "recommendations": _dedupe(recommendations),
        "linking_strategy": "Each recommendation includes related_findings with finding IDs.",
    }
