"""
Contextual Analysis Model (Model 3): incorporate age/gender to adjust risk and add notes.
"""
from models.model2_ml_risk import calculate_total_risk, get_severity

def adjust_by_context(row, base_score):
    age = int(row.get("Age", 35))
    gender = (row.get("Gender") or "Male").strip().lower()
    adj = base_score
    if age > 60:
        adj += 1
    if gender == "male":
        adj += 0.5
    return adj

def contextual_adjustment(data, age=None, gender=None):
    """
    Incorporate user context (age, gender) into risk and return context flags for synthesis.
    data: validated dict with numeric params (and optionally Age, Gender).
    Returns dict: adjusted_score, risk_level, context_notes.
    """
    row = dict(data)
    a = age if age is not None else row.get("Age", 35)
    g = (gender or row.get("Gender") or "Male").strip()
    row["Age"] = a
    row["Gender"] = g
    base_score = calculate_total_risk(row)
    adjusted_score = adjust_by_context(row, base_score)
    risk_level = get_severity(adjusted_score)
    notes = []
    if a > 60:
        notes.append("Age over 60 considered in risk assessment.")
    if g.lower() == "male":
        notes.append("Male reference context applied.")
    return {
        "adjusted_score": adjusted_score,
        "risk_level": risk_level,
        "context_notes": notes,
    }
