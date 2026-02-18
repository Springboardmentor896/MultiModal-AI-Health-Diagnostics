from datetime import datetime
DISCLAIMER = """
This AI-generated report provides supportive health insights based on the
submitted laboratory values. It is NOT a medical diagnosis and should not
replace consultation with a qualified healthcare professional.
Please consult a licensed physician for clinical interpretation.
"""

def format_parameter_section(parameters):
    lines = []
    for param, details in parameters.items():
        line = f"{param}: {details['value']} ({details['status']})"
        lines.append(line)
    return "\n".join(lines)

def format_summary_section(summary):
    lines = []
    
    if summary["abnormal_parameters"]:
        lines.append("Abnormal Parameters:")
        for p in summary["abnormal_parameters"]:
            lines.append(f" - {p}")
    else:
        lines.append("All major parameters are within reference ranges.")
        
    lines.append(f"\nEstimated Risk Level: {summary['risk_level']}")
    lines.append(f"Risk Probability Score: {summary['risk_probability']}")
    
    if summary["context_notes"]:
        lines.append("\nContextual Notes:")
        for note in summary["context_notes"]:
            lines.append(f" - {note}")
            
    return "\n".join(lines)

def format_recommendations(recommendations):
    if not recommendations:
        return "No specific recommendations generated."
        
    lines = ["Recommended Actions:"]
    for r in recommendations:
        lines.append(f" - {r}")
    return "\n".join(lines)

def generate_full_report(parameters, summary, recommendations, confidence):
    report = f"""
==========================================================
AI HEALTH DIAGNOSTIC REPORT
Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}
==========================================================

--- Parameter Interpretation ---
{format_parameter_section(parameters)}

--- Analytical Summary ---
{format_summary_section(summary)}

--- Personalized Recommendations ---
{format_recommendations(recommendations)}

--- System Confidence ---
Confidence Score: {confidence}%

--- Disclaimer ---
{DISCLAIMER}

==========================================================
End of Report
==========================================================
"""
    return report