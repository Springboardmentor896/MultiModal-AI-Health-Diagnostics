import ollama

class ReportSynthesizer:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate_report(self, profile, risks, recs, data):
        """
        Synthesizes the final report using Local Ollama (Free/Unlimited).
        """
        abnormal_findings = [
            f"- {item['Standard_Name']}: {item['Value']} {item['Unit']} ({item['Flag']})" 
            for item in data if item['Status'] == 'Abnormal'
        ]
        
        risk_str = ", ".join([f"{r['Condition']} ({r['Risk']})" for r in risks]) if risks else "No specific disease patterns detected."
        
        prompt = f"""
        You are an expert Medical AI. Write a diagnostic summary for:
        
        PATIENT: {profile['name']} ({profile['age']} {profile['gender']})
        STATUS: {'Pregnant' if profile['is_pregnant'] else 'Not Pregnant'}
        
        DETECTED RISKS: {risk_str}
        
        KEY ABNORMALITIES:
        {chr(10).join(abnormal_findings)}
        
        RECOMMENDED ACTIONS:
        - {", ".join(recs.get('medical', [])[:2])}
        - {", ".join(recs.get('diet', [])[:2])}

        TASK:
        Write a professional 3-paragraph clinical summary.
        1. Clinical Impression (What is the main issue?)
        2. Significant Findings (What data supports this?)
        3. Action Plan (What should they do?)
        
        Keep it under 200 words. Be empathetic but professional.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error generating report: {str(e)}. Please ensure Ollama is running."
