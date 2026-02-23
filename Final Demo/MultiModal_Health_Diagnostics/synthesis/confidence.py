from typing import Dict, Any

def calculate_confidence(
    extracted: Dict[str, Any],
    interpreted: Dict[str, Any],
    risks: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate confidence score based on:
    - Parameter coverage (how many params extracted vs expected)
    - Data quality (valid vs unknown status)
    - Risk signal strength (probability distribution)
    
    Returns: {score: 0-100, level: low/medium/high, reasons: [...]}
    """
    # Expected critical parameters (from teacher requirements)
    CRITICAL_PARAMS = ['Hemoglobin', 'Fasting_Glucose', 'Total_Cholesterol', 'WBC', 'Platelets']
    TOTAL_EXPECTED = 20  # We have 20 params in parameterranges.json
    
    # 1. Coverage score (40% weight)
    extracted_count = len(extracted)
    coverage_pct = (extracted_count / TOTAL_EXPECTED) * 100
    coverage_score = min(40, coverage_pct * 0.4)  # Max 40 points
    
    # 2. Data quality (30% weight)
    valid_count = sum(1 for p in interpreted.values() if p.get('status') != 'unknown')
    quality_pct = (valid_count / max(1, len(interpreted))) * 100
    quality_score = min(30, quality_pct * 0.3)  # Max 30 points
    
    # 3. Critical params present (20% weight)
    critical_present = sum(1 for p in CRITICAL_PARAMS if p in interpreted and interpreted[p].get('status') != 'unknown')
    critical_score = (critical_present / len(CRITICAL_PARAMS)) * 20  # Max 20 points
    
    # 4. Risk signal strength (10% weight)
    high_risk_count = sum(1 for r in risks.values() if r.get('label') == 'high')
    risk_signal_score = min(10, high_risk_count * 2)  # Max 10 points
    
    # Total confidence
    total_score = coverage_score + quality_score + critical_score + risk_signal_score
    
    # Level classification
    if total_score >= 80:
        level = "high"
    elif total_score >= 50:
        level = "medium"
    else:
        level = "low"
    
    # Detailed reasons
    reasons = [
        f"Parameter coverage: {extracted_count}/{TOTAL_EXPECTED} extracted ({coverage_pct:.0f}%)",
        f"Data quality: {valid_count}/{len(interpreted)} valid ({quality_pct:.0f}%)",
        f"Critical params: {critical_present}/{len(CRITICAL_PARAMS)} present",
        f"High risk signals: {high_risk_count}"
    ]
    
    # Warnings
    missing_critical = [p for p in CRITICAL_PARAMS if p not in interpreted or interpreted[p].get('status') == 'unknown']
    if missing_critical:
        reasons.append(f"⚠️ Missing critical: {', '.join(missing_critical)}")
    
    return {
        "score": round(total_score, 1),
        "level": level,
        "reasons": reasons,
        "breakdown": {
            "coverage": round(coverage_score, 1),
            "quality": round(quality_score, 1),
            "critical": round(critical_score, 1),
            "risk_signal": round(risk_signal_score, 1)
        }
    }
