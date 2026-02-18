import ollama

def infer_intent(user_input, history):
   
    clinical_keywords = ["hemoglobin", "glucose", "wbc", "platelets", "mg/dl", "g/dl"]
    if any(keyword in user_input.lower() for keyword in clinical_keywords):
        return "analyze_report"

    prompt = f"Analyze intent: 'analyze_report' or 'ask_general_health_question'. Input: {user_input}"
    
    try:
        response = ollama.chat(model='tinydolphin', messages=[
            {'role': 'user', 'content': prompt},
        ])
        result = response['message']['content'].lower()
        
        if "report" in result or "analyze" in result:
            return "analyze_report"
        return "ask_general_health_question"
    except Exception:
        return "ask_general_health_question"