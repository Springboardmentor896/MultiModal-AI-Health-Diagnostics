import ollama

class QAEngine:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.context_memory = ""

    def set_context(self, profile, risks, data, report_summary):
        abnormal_str = ", ".join([f"{d['Standard_Name']} {d['Value']} ({d['Flag']})" for d in data if d['Status'] == 'Abnormal'])
        
        self.context_memory = f"""
        Patient: {profile['name']}, {profile['age']} yrs, {profile['gender']}.
        Risks: {[r['Condition'] for r in risks]}.
        Abnormalities: {abnormal_str}.
        Summary: {report_summary}
        """

    def ask_question(self, user_question):
        if not self.context_memory:
            return "Please upload a report first."

        prompt = f"""
        Context: {self.context_memory}
        Question: {user_question}
        Answer strictly based on the context. Be concise (max 2 sentences).
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"
