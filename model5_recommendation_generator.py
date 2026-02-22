"""
💊 RECOMMENDATION GENERATOR ENGINE
Converts clinical findings → actionable lifestyle advice

Core Logic:
Finding → Recommended Action
Elevated glucose → Diet + Exercise + Testing
High cholesterol → Low-fat diet + Cardio
Low hemoglobin → Iron-rich foods + Doctor visit
"""

import json
from typing import Dict, List, Any

class RecommendationGenerator:
    """Generates personalized health recommendations"""

    def __init__(self):
        # Comprehensive recommendation mapping
        self.recommendation_rules = {
            "glucose": {
                "High": [
                    "Reduce intake of sugary foods and refined carbohydrates",
                    "Increase physical activity (30 min daily aerobic exercise)",
                    "Schedule HbA1c testing to monitor long-term glucose control",
                    "Consider consulting an endocrinologist"
                ],
                "Low": [
                    "Increase carbohydrate intake",
                    "Keep sugary drinks/glucose tablets available",
                    "Monitor blood sugar levels regularly"
                ]
            },
            "cholesterol": {
                "High": [
                    "Adopt a low-fat, high-fiber diet (reduce saturated fats)",
                    "Include daily cardiovascular exercise (brisk walking 45 min)",
                    "Consult physician for lipid management and possible medication",
                    "Increase intake of omega-3 rich foods (fish, flax seeds)"
                ],
                "Low": [
                    "Ensure adequate healthy fat intake",
                    "Monitor nutritional status"
                ]
            },
            "hemoglobin": {
                "Low": [
                    "Increase iron-rich foods (spinach, red meat, lentils, dates)",
                    "Include vitamin C sources to enhance iron absorption (citrus)",
                    "Schedule ferritin and iron panel testing",
                    "Consult doctor if fatigue persists beyond 4 weeks",
                    "Consider iron supplementation if dietary changes insufficient"
                ],
                "High": [
                    "Monitor hydration status",
                    "Consider phlebotomy if significantly elevated"
                ]
            },
            "white_blood_cells": {
                "High": [
                    "Monitor for signs of infection or inflammation",
                    "Consider blood culture if fever present",
                    "Rest and increase fluid intake",
                    "Schedule follow-up testing in 1 week"
                ],
                "Low": [
                    "Avoid sick individuals and crowds",
                    "Practice strict hygiene",
                    "Consult hematologist for immune support"
                ]
            },
            "platelet_count": {
                "Low": [
                    "Avoid NSAIDs and blood thinners",
                    "Take precautions against bleeding (soft toothbrush)",
                    "Report any unusual bruising or bleeding",
                    "Schedule coagulation panel testing"
                ],
                "High": [
                    "Increase hydration",
                    "Monitor for blood clot symptoms"
                ]
            }
        }

        # General recommendations by age
        self.age_based_recommendations = {
            "young": "Focus on preventive health and establishing good habits",
            "middle": "Balance family/work stress and maintain regular checkups",
            "senior": "Prioritize bone health, cardiovascular fitness, and medication review",
            "elderly": "Focus on fall prevention, medication adherence, and regular monitoring"
        }

    def get_age_group(self, age: int) -> str:
        """Classify age group"""
        if age <= 35: return "young"
        if age <= 50: return "middle"
        if age <= 65: return "senior"
        return "elderly"

    def generate_recommendations(self, synthesis: Dict) -> Dict[str, Any]:
        """
        Generate personalized recommendations from clinical synthesis

        Args:
            synthesis: Output from FindingsSynthesisEngine

        Returns:
            Detailed recommendation plan
        """
        recommendations = []
        priority_actions = []

        # Extract findings and map to recommendations
        findings = synthesis.get("key_findings", [])

        for finding in findings:
            finding_lower = finding.lower()

            # Check each recommendation category
            for param_key, rules in self.recommendation_rules.items():
                if param_key in finding_lower:
                    # Determine High/Low status
                    if "high" in finding_lower or "elevated" in finding_lower:
                        recs = rules.get("High", [])
                    elif "low" in finding_lower:
                        recs = rules.get("Low", [])
                    else:
                        recs = list(rules.values())[0]

                    recommendations.extend(recs)

        # High-risk immediate actions
        risk_level = synthesis.get("overall_risk_level", "Low")
        if risk_level in ["High", "Critical"]:
            priority_actions = [
                "Schedule urgent medical consultation",
                "Monitor vital signs daily",
                "Avoid strenuous activity until evaluated"
            ]

        # Age-based recommendations
        age = synthesis["patient_context"].get("age", 40)
        age_group = self.get_age_group(age)
        age_rec = self.age_based_recommendations.get(age_group)

        # Build recommendation plan
        plan = {
            "priority_actions": priority_actions,
            "lifestyle_modifications": list(set(recommendations)),  # Remove duplicates
            "age_appropriate_focus": age_rec,
            "follow_up_schedule": self.generate_followup_schedule(risk_level),
            "total_recommendations": len(recommendations),
            "risk_level": risk_level
        }

        return plan

    def generate_followup_schedule(self, risk_level: str) -> Dict[str, str]:
        """Generate testing schedule based on risk"""
        schedules = {
            "Low": {
                "routine_checkup": "Annually",
                "blood_tests": "Every 2 years",
                "lifestyle_review": "Annually"
            },
            "Medium": {
                "routine_checkup": "Every 6 months",
                "blood_tests": "Every 6 months",
                "specialist_consultation": "Within 3 months"
            },
            "High": {
                "routine_checkup": "Monthly",
                "blood_tests": "Monthly",
                "specialist_consultation": "Within 2 weeks",
                "emergency_contact": "Establish with physician"
            },
            "Critical": {
                "emergency_consultation": "Immediately",
                "hospital_evaluation": "Same day",
                "24hr_monitoring": "Consider admission"
            }
        }

        return schedules.get(risk_level, schedules["Low"])

# TEST
if __name__ == "__main__":
    gen = RecommendationGenerator()

    synthesis = {
        "patient_context": {"age": 55, "gender": "Male"},
        "key_findings": [
            "Elevated blood glucose indicating diabetes risk",
            "High cholesterol increasing cardiovascular risk"
        ],
        "overall_risk_level": "High"
    }

    plan = gen.generate_recommendations(synthesis)
    print("\n=== RECOMMENDATION GENERATOR ===")
    print(json.dumps(plan, indent=2))
