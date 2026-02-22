from typing import Literal

Intent = Literal["general_checkup", "anemia_focus", "infection_focus", "bleeding_risk", "unknown"]

class IntentInferenceModel:
    def infer_intent(self, user_message: str) -> Intent:
        text = user_message.lower()
        if any(word in text for word in ["anemia", "hemoglobin", "iron"]):
            return "anemia_focus"
        if any(word in text for word in ["infection", "wbc", "fever", "leukocyte"]):
            return "infection_focus"
        if any(word in text for word in ["bleeding", "platelets", "bruising"]):
            return "bleeding_risk"
        if any(word in text for word in ["checkup", "review", "analyze"]):
            return "general_checkup"
        return "unknown"

if __name__ == "__main__":
    model = IntentInferenceModel()
    test_messages = [
        "Check my hemoglobin - worried about anemia",
        "High WBC on my report, is it infection?",
        "Low platelets, bleeding risk?",
        "General blood work review please"
    ]
    for msg in test_messages:
        print(f"Message: '{msg}' -> Intent: {model.infer_intent(msg)}")
