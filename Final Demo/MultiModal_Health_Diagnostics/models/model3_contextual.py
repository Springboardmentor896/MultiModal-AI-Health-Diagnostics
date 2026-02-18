"""
Model 3: Contextual Risk Aggregator
Combines Model 1 (Clinical Rules) + Model 2 (ML Risk) with patient context
"""


class Model3Contextual:
    def __init__(self):
        self.name = "Contextual_Aggregator"

        # How much weight each model gets in final score
        self.model_weights = {
            'model1': 0.45,  # Clinical rules - high trust
            'model2': 0.55   # ML risk - slightly higher for data-driven
        }

        # Age-based risk multipliers
        self.age_risk_multipliers = {
            'cardiovascular': [(0, 30, 0.7), (30, 50, 1.0), (50, 70, 1.3), (70, 120, 1.6)],
            'diabetes':        [(0, 30, 0.8), (30, 50, 1.0), (50, 70, 1.2), (70, 120, 1.4)],
            'hypertension':    [(0, 30, 0.8), (30, 50, 1.0), (50, 70, 1.3), (70, 120, 1.5)],
            'kidney_dysfunction': [(0, 40, 0.9), (40, 60, 1.1), (60, 120, 1.3)],
            'liver_dysfunction':  [(0, 40, 0.9), (40, 60, 1.0), (60, 120, 1.2)],
            'anemia':          [(0, 18, 1.2), (18, 60, 1.0), (60, 120, 1.2)],
            'infection':       [(0, 5,  1.3), (5, 60, 1.0), (60, 120, 1.2)],
            'thyroid_dysfunction': [(0, 120, 1.0)]
        }

        # Gender-based risk multipliers
        self.gender_risk_multipliers = {
            'anemia': {'female': 1.2, 'male': 1.0},
            'cardiovascular': {'male': 1.2, 'female': 1.0},
            'hypertension': {'male': 1.1, 'female': 1.0},
            'thyroid_dysfunction': {'female': 1.3, 'male': 1.0},
            'infection': {'male': 1.0, 'female': 1.0},
            'diabetes': {'male': 1.0, 'female': 1.0},
            'kidney_dysfunction': {'male': 1.1, 'female': 1.0},
            'liver_dysfunction': {'male': 1.1, 'female': 1.0}
        }

        # Pregnancy risk multipliers
        self.pregnancy_multipliers = {
            'anemia': 1.5,
            'hypertension': 1.4,
            'diabetes': 1.3,
            'kidney_dysfunction': 1.2,
            'thyroid_dysfunction': 1.3,
            'cardiovascular': 1.2,
            'infection': 1.2,
            'liver_dysfunction': 1.1
        }

        # Disease co-occurrence boosts
        # If disease A is high risk, boost disease B
        self.comorbidity_boosts = {
            'anemia': {'kidney_dysfunction': 0.05, 'cardiovascular': 0.05},
            'infection': {'kidney_dysfunction': 0.05, 'liver_dysfunction': 0.04},
            'diabetes': {'cardiovascular': 0.08, 'kidney_dysfunction': 0.07, 'hypertension': 0.06},
            'hypertension': {'cardiovascular': 0.08, 'kidney_dysfunction': 0.05},
            'kidney_dysfunction': {'cardiovascular': 0.06, 'hypertension': 0.05},
            'liver_dysfunction': {'infection': 0.04, 'kidney_dysfunction': 0.04},
            'cardiovascular': {'hypertension': 0.05, 'diabetes': 0.04},
            'thyroid_dysfunction': {'cardiovascular': 0.04, 'diabetes': 0.03}
        }

    def analyze(self, lab_data, patient_info, model1_results, model2_results):
        """
        Combine M1 + M2 results with patient context into final risk scores
        """
        age = patient_info.get('age', 30)
        gender = patient_info.get('gender', 'male').lower()
        pregnant = patient_info.get('pregnant', False)

        m1_risks = model1_results.get('risks', {})
        m2_risks = model2_results.get('risks', {})

        all_diseases = set(m1_risks.keys()) | set(m2_risks.keys())

        # Step 1: Weighted average of M1 + M2
        combined = {}
        for disease in all_diseases:
            p1 = m1_risks.get(disease, {}).get('probability', 0.05)
            p2 = m2_risks.get(disease, {}).get('probability', 0.05)
            combined[disease] = (
                self.model_weights['model1'] * p1 +
                self.model_weights['model2'] * p2
            )

        # Step 2: Apply age multiplier
        for disease in combined:
            multiplier = self._get_age_multiplier(disease, age)
            combined[disease] = min(0.95, combined[disease] * multiplier)

        # Step 3: Apply gender multiplier
        for disease in combined:
            g_mult = self.gender_risk_multipliers.get(disease, {}).get(gender, 1.0)
            combined[disease] = min(0.95, combined[disease] * g_mult)

        # Step 4: Apply pregnancy multiplier
        if pregnant and gender == 'female':
            for disease in combined:
                p_mult = self.pregnancy_multipliers.get(disease, 1.0)
                combined[disease] = min(0.95, combined[disease] * p_mult)

        # Step 5: Apply comorbidity boosts
        # Only boost if primary disease is already elevated (>20%)
        boosts = {d: 0.0 for d in combined}
        for primary_disease, targets in self.comorbidity_boosts.items():
            if combined.get(primary_disease, 0) > 0.20:
                for target, boost in targets.items():
                    if target in boosts:
                        boosts[target] += boost

        for disease in combined:
            combined[disease] = min(0.95, combined[disease] + boosts[disease])

        # Step 6: Build final output
        final_risks = {}
        for disease, prob in combined.items():
            final_risks[disease] = {
                'probability': round(prob, 3),
                'label': self._risk_label(prob * 100),
                'contributing_models': {
                    'model1': round(m1_risks.get(disease, {}).get('probability', 0.05), 3),
                    'model2': round(m2_risks.get(disease, {}).get('probability', 0.05), 3)
                }
            }

        # Step 7: Compute overall risk
        all_probs = [r['probability'] for r in final_risks.values()]
        max_prob = max(all_probs) if all_probs else 0.05

        if max_prob >= 0.50:
            overall = 'high'
        elif max_prob >= 0.20:
            overall = 'moderate'
        else:
            overall = 'low'

        return {
            'model': self.name,
            'risks': final_risks,
            'overall_risk': overall,
            'overall_probability': round(max_prob, 3)
        }

    def _get_age_multiplier(self, disease, age):
        """Look up age bracket multiplier for a disease"""
        brackets = self.age_risk_multipliers.get(disease, [(0, 120, 1.0)])
        for low, high, mult in brackets:
            if low <= age < high:
                return mult
        return 1.0

    def _risk_label(self, score):
        """Convert probability % to label"""
        if score >= 50:
            return 'high'
        elif score >= 20:
            return 'moderate'
        else:
            return 'low'
