import ollama

def generate_recommendations(summary, rag_context=None):
    system_message = (
        """You are a Clinical Health Assistant. Your output MUST be in professional Markdown. 
        Use bullet points for lists. Do NOT repeat these instructions in your response. 
        Avoid medical jargon where possible. If the question is not about the report, respond with: I can only answer questions related to the provided medical report."""
    )
    
    prompt = f"""
    ### INSTRUCTIONS:
    DO NOT answer unrelated questions or provide programming/political/financial content.
    Analyze the provided Clinical Summary and Guidelines to give lifestyle advice.
    Structure the report with the exact headers provided below.

    ### CLINICAL SUMMARY:
    {summary}

    ### MEDICAL GUIDELINES:
    {rag_context if rag_context else "Standard health practices."}

    ### OUTPUT FORMAT:
    ###  Clinical Interpretation
    ###  Dietary Suggestions
    ###  Lifestyle & Exercise
    ###  Important Risks
    """
    
    try:
        response = ollama.chat(model='tinydolphin', messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': prompt},
        ])
        return [response['message']['content']]
    except Exception as e:
        return [f"Ollama Error: {str(e)}"]

def generate_general_health_response(user_input):
    try:
        response = ollama.chat(model='tinydolphin', messages=[
            {'role': 'system', 'content': 'You are a helpful health assistant.'},
            {'role': 'user', 'content': user_input},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Ollama Error: {str(e)}"