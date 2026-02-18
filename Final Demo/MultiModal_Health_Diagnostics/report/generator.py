"""
Report Generator - Produces downloadable diagnostic report
"""

from datetime import datetime


REFERENCE_RANGES = {
    'male': {
        'hemoglobin':   (13.0, 17.0,   'g/dL'),
        'rbc':          (4.5,  5.5,    'mill/cumm'),
        'wbc':          (4000, 11000,  'cumm'),
        'platelets':    (150000, 410000, 'cumm'),
        'pcv':          (40.0, 50.0,   '%'),
        'mcv':          (83.0, 101.0,  'fL'),
        'mch':          (27.0, 32.0,   'pg'),
        'mchc':         (32.5, 34.5,   'g/dL'),
        'rdw':          (11.6, 14.0,   '%'),
        'neutrophils':  (50.0, 62.0,   '%'),
        'lymphocytes':  (20.0, 40.0,   '%'),
        'monocytes':    (0.0,  10.0,   '%'),
        'eosinophils':  (0.0,  6.0,    '%'),
        'basophils':    (0.0,  2.0,    '%'),
    },
    'female': {
        'hemoglobin':   (12.0, 16.0,   'g/dL'),
        'rbc':          (4.0,  5.0,    'mill/cumm'),
        'wbc':          (4000, 11000,  'cumm'),
        'platelets':    (150000, 410000, 'cumm'),
        'pcv':          (36.0, 46.0,   '%'),
        'mcv':          (83.0, 101.0,  'fL'),
        'mch':          (27.0, 32.0,   'pg'),
        'mchc':         (32.5, 34.5,   'g/dL'),
        'rdw':          (11.6, 14.0,   '%'),
        'neutrophils':  (50.0, 62.0,   '%'),
        'lymphocytes':  (20.0, 40.0,   '%'),
        'monocytes':    (0.0,  10.0,   '%'),
        'eosinophils':  (0.0,  6.0,    '%'),
        'basophils':    (0.0,  2.0,    '%'),
    }
}


class ReportGenerator:
    """Backward compatible with orchestrator."""

    def generate(self, patient_info=None, lab_data=None, analysis=None,
                 model3_results=None, query=None, **kwargs):
        """
        Called by orchestrator as:
            self.report_generator.generate(
                patient_info=patient_info,
                lab_data=lab_data,
                analysis=synthesis,
                query=query
            )

        synthesis dict structure:
            {
                'patient': ...,
                'lab_data': ...,
                'risks': { disease: {probability, label} },   ← per-disease risks
                'synthesis_summary': {
                    'key_findings': [...],
                    'overall_risk': 'low'/'moderate'/'high',
                    'risk_score': 0.057,
                    'risk_probability': 5.7                   ← already in %
                },
                'recommendations': [...],
                'model_outputs': ...
            }
        """

        if model3_results is None and analysis is not None:
            summary      = analysis.get('synthesis_summary', {})
            model3_risks = analysis.get('risks', {})
            # Merge synthesis_summary (has overall risk)
            # with analysis risks (has per-disease breakdown)
            model3_results = {**summary, 'risks': model3_risks}

        # Fallbacks
        if model3_results is None:
            model3_results = {}
        if lab_data is None:
            lab_data = {}
        if patient_info is None:
            patient_info = {'age': 30, 'gender': 'male', 'pregnant': False}

        report_text = generate_report(lab_data, patient_info, model3_results)

        return {
            'report_text': report_text,
            'patient_info': patient_info,
            'lab_data': lab_data
        }


def get_key_findings(lab_data, patient_info):
    """Extract key abnormal findings directly from lab values."""
    findings = []
    gender = patient_info.get('gender', 'male').lower()
    ranges = REFERENCE_RANGES.get(gender, REFERENCE_RANGES['male'])

    for param, value in lab_data.items():
        if param not in ranges:
            continue
        low, high, unit = ranges[param]
        if value < low:
            findings.append(
                f"{param.replace('_', ' ').title()} is low "
                f"({value} vs {low}-{high} {unit})"
            )
        elif value > high:
            findings.append(
                f"{param.replace('_', ' ').title()} is high "
                f"({value} vs {low}-{high} {unit})"
            )

    return findings if findings else ["All parameters within normal range."]


def get_recommendations(lab_data, model3_results, patient_info):
    """Generate recommendations based on actual lab values and risk scores."""
    recs     = []
    gender   = patient_info.get('gender', 'male').lower()
    pregnant = patient_info.get('pregnant', False)
    ranges   = REFERENCE_RANGES.get(gender, REFERENCE_RANGES['male'])

    # --- Hemoglobin ---
    hb = lab_data.get('hemoglobin')
    if hb is not None:
        hb_low = ranges['hemoglobin'][0]
        if hb < hb_low:
            recs.append(
                f"Hemoglobin ({hb} g/dL) is below normal ({hb_low} g/dL). "
                "Suggest iron-rich diet (leafy greens, red meat, legumes), "
                "consider iron supplementation, and follow up with a physician "
                "to rule out anemia."
            )

    # --- WBC ---
    wbc = lab_data.get('wbc')
    if wbc is not None:
        if wbc > 11000:
            recs.append(
                f"WBC count ({wbc}) is elevated. This may indicate infection "
                "or inflammation. Consult a physician for further evaluation."
            )
        elif wbc < 4000:
            recs.append(
                f"WBC count ({wbc}) is low, which may indicate compromised "
                "immunity. Consult a physician promptly."
            )

    # --- Platelets ---
    platelets = lab_data.get('platelets')
    if platelets is not None:
        if platelets < 150000:
            recs.append(
                f"Platelet count ({int(platelets)}) is low (thrombocytopenia). "
                "Avoid NSAIDs/aspirin, monitor for unusual bruising or bleeding, "
                "and consult a hematologist."
            )
        elif platelets == 150000:
            recs.append(
                f"Platelet count ({int(platelets)}) is at the borderline lower "
                "limit. Monitor and recheck in 4-6 weeks."
            )

    # --- PCV ---
    pcv = lab_data.get('pcv')
    if pcv is not None:
        pcv_low  = ranges['pcv'][0]
        pcv_high = ranges['pcv'][1]
        if pcv > pcv_high:
            recs.append(
                f"PCV ({pcv}%) is above normal range ({pcv_low}-{pcv_high}%). "
                "Elevated PCV may indicate dehydration or polycythemia. "
                "Increase fluid intake and consult a doctor."
            )
        elif pcv < pcv_low:
            recs.append(
                f"PCV ({pcv}%) is below normal ({pcv_low}-{pcv_high}%). "
                "This supports possible anemia findings."
            )

    # --- Neutrophils ---
    neutrophils = lab_data.get('neutrophils')
    if neutrophils is not None and neutrophils > 70:
        recs.append(
            f"Neutrophil count ({neutrophils}%) is elevated, which may suggest "
            "bacterial infection or stress response."
        )

    # --- Lymphocytes ---
    lymphocytes = lab_data.get('lymphocytes')
    if lymphocytes is not None and lymphocytes < 20:
        recs.append(
            f"Lymphocyte count ({lymphocytes}%) is low (lymphopenia). "
            "This may affect immune response."
        )

    # --- Risk-based recommendations ---
    risks = model3_results.get('risks', {})
    for disease, risk in risks.items():
        prob  = risk.get('probability', 0)
        label = risk.get('label', 'low')
        if label == 'high':
            recs.append(
                f"{disease.replace('_', ' ').title()} risk is HIGH "
                f"({prob*100:.1f}%). Immediate medical consultation is strongly "
                "recommended."
            )
        elif label == 'moderate':
            recs.append(
                f"{disease.replace('_', ' ').title()} risk is MODERATE "
                f"({prob*100:.1f}%). Schedule a follow-up with your doctor "
                "within 2-4 weeks."
            )

    # --- Pregnancy ---
    if pregnant:
        recs.append(
            "Patient is pregnant. All findings should be reviewed by an OB-GYN. "
            "Anemia and borderline values are more critical during pregnancy."
        )

    # --- Fallback ---
    if not recs:
        recs.append(
            "All parameters are within acceptable ranges. Maintain a healthy "
            "lifestyle with balanced diet, regular exercise, and routine "
            "checkups every 6-12 months."
        )

    return recs


def generate_report(lab_data, patient_info, model3_results):
    """
    Generate full text report using Model 3 results,
    real reference ranges, and smart recommendations.
    """
    gender = patient_info.get('gender', 'male').lower()
    ranges = REFERENCE_RANGES.get(gender, REFERENCE_RANGES['male'])

    overall_risk = model3_results.get('overall_risk', 'low').upper()

    # FIX: synthesis_summary uses 'risk_probability' (already in %)
    # Model 3 direct output uses 'overall_probability' (0.0 - 1.0 scale)
    if 'risk_probability' in model3_results:
        overall_prob = float(model3_results['risk_probability'])
    elif 'overall_probability' in model3_results:
        overall_prob = float(model3_results['overall_probability']) * 100
    else:
        overall_prob = 5.0  # safe default

    key_findings    = get_key_findings(lab_data, patient_info)
    recommendations = get_recommendations(lab_data, model3_results, patient_info)

    lines = []
    lines.append("=" * 60)
    lines.append("HEALTH DIAGNOSTIC REPORT")
    lines.append("=" * 60)

    # --- Patient Info ---
    lines.append("\nPATIENT INFORMATION")
    lines.append("-" * 60)
    lines.append(f"Name:        {patient_info.get('name', 'Patient')}")
    lines.append(f"Age:         {patient_info.get('age', 'N/A')}")
    lines.append(f"Gender:      {patient_info.get('gender', 'N/A').title()}")
    lines.append(f"Pregnant:    {patient_info.get('pregnant', False)}")
    lines.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # --- Overall Assessment ---
    lines.append("\nOVERALL ASSESSMENT")
    lines.append("-" * 60)
    lines.append(f"Risk Score:  {overall_prob:.1f}% ({overall_risk})")

    # --- Lab Parameters ---
    lines.append("\nLAB PARAMETERS")
    lines.append("-" * 60)
    lines.append(
        f"{'Parameter':<20} {'Value':>10}  "
        f"{'Reference Range':<22} {'Unit':<12} {'Status'}"
    )
    lines.append("-" * 78)

    for param, value in lab_data.items():
        if param in ranges:
            low, high, unit = ranges[param]
            ref_str = f"{low} - {high}"
            if value < low:
                status = "LOW ⬇"
            elif value > high:
                status = "HIGH ⬆"
            else:
                status = "Normal ✓"
        else:
            ref_str = "N/A"
            unit    = ""
            status  = ""
        lines.append(
            f"{param:<20} {str(value):>10}  {ref_str:<22} {unit:<12} {status}"
        )

    # --- Disease Risk Analysis ---
    lines.append("\nDISEASE RISK ANALYSIS")
    lines.append("-" * 60)
    risks = model3_results.get('risks', {})
    if risks:
        for disease, risk in sorted(
            risks.items(),
            key=lambda x: x[1]['probability'],
            reverse=True
        ):
            prob  = risk['probability'] * 100
            label = risk['label'].upper()
            icon  = "🔴" if label == "HIGH" else ("🟡" if label == "MODERATE" else "🟢")
            lines.append(
                f"{icon} {disease.replace('_', ' ').title():<25} "
                f"{prob:.1f}%  ({label})"
            )
    else:
        lines.append("No disease risk data available.")

    # --- Key Findings ---
    lines.append("\nKEY FINDINGS")
    lines.append("-" * 60)
    for f in key_findings:
        lines.append(f"• {f}")

    # --- Recommendations ---
    lines.append("\nRECOMMENDATIONS")
    lines.append("-" * 60)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")

    lines.append("\n" + "=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    return "\n".join(lines)
