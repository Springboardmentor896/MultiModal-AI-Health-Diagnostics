from groq import Groq


class HealthChatAssistant:
    def __init__(self):
        self.api_key = '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'
        self.client = Groq(api_key=self.api_key)
        self.model = 'llama-3.3-70b-versatile'


    def generate_clinical_recommendations(self, lab_data, risks, patient_info):
        context = self._build_clinical_context(lab_data, risks, patient_info)
        prompt = f"Clinical findings:\n{context}\n\nProvide evidence-based clinical recommendations with specific tests, dietary advice, and lifestyle modifications."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f'Error: {str(e)}'


    def chat_with_report(self, user_question, lab_data, risks, patient_info, chat_history):
        # ==============================================================
        # MEDICAL QUESTION FILTER - Check before calling API
        # ==============================================================
        
        if not self._is_medical_question(user_question):
            return """
⚠️ **I can only answer medical and health-related questions.**

**I specialize in:**
- 🩺 Laboratory test results and parameters
- 💊 Medical conditions and diseases  
- 🧬 Health concerns and symptoms
- 🏥 When to seek medical care

**I cannot help with:**
- ❌ Travel, places, or geography
- ❌ Products, cars, bikes, or brands
- ❌ Entertainment, sports, or movies
- ❌ General knowledge or non-medical topics

**Please ask about your lab results or health concerns.**

**Examples:**
- "What does high hemoglobin mean?"
- "Is my glucose level concerning?"
- "What foods help improve my results?"
- "Should I see a doctor about these findings?"
"""
        
        # ==============================================================
        # PROCEED WITH MEDICAL RESPONSE
        # ==============================================================
        
        context = self._build_clinical_context(lab_data, risks, patient_info)
        
        messages = [{'role': 'system', 'content': f'Medical context:\n{context}\n\nYou are a medical AI assistant. Provide professional, evidence-based advice.'}]
        for msg in chat_history[-10:]:
            messages.append({'role': msg['role'], 'content': msg['content']})
        messages.append({'role': 'user', 'content': user_question})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=1000
            )
            answer = response.choices[0].message.content
            
            # Add medical disclaimer
            answer += "\n\n---\n⚕️ **Disclaimer:** Consult a healthcare professional for medical advice."
            
            return answer
        except Exception as e:
            return f'Error: {str(e)}'


    def _is_medical_question(self, question):
        """
        Check if question is medical/health-related
        Returns True if medical, False otherwise
        """
        
        question_lower = question.lower().strip()
        
        # Medical keywords whitelist
        medical_keywords = [
            # Lab parameters
            'hemoglobin', 'hb', 'glucose', 'sugar', 'cholesterol', 'ldl', 'hdl',
            'creatinine', 'wbc', 'rbc', 'platelet', 'hba1c', 'a1c', 'tsh',
            'alt', 'sgpt', 'ast', 'sgot', 'bilirubin', 'albumin', 'protein',
            
            # Body systems
            'blood', 'heart', 'kidney', 'liver', 'lung', 'thyroid',
            
            # Medical conditions
            'anemia', 'diabetes', 'hypertension', 'pressure', 'infection',
            'disease', 'disorder', 'syndrome',
            
            # Symptoms
            'pain', 'fever', 'sick', 'ill', 'symptom', 'tired', 'fatigue',
            
            # Lab context
            'lab', 'test', 'result', 'report', 'parameter', 'value',
            'abnormal', 'normal', 'high', 'low', 'elevated', 'decreased',
            'risk', 'level', 'count', 'range',
            
            # Healthcare
            'doctor', 'hospital', 'clinic', 'physician', 'medical',
            'health', 'treatment', 'medication', 'medicine', 'drug',
            'diagnosis', 'concern', 'worried', 'advice', 'recommend',
            
            # Health-related diet and lifestyle
            'diet', 'eat', 'food', 'nutrition', 'supplement', 'vitamin',
            'exercise', 'lifestyle', 'sleep', 'stress', 'weight',
            'improve', 'prevent', 'avoid', 'should i', 'can i',
            'my results', 'my report', 'my lab', 'my test'
        ]
        
        # Check if question has ANY medical keyword
        has_medical_keyword = any(keyword in question_lower for keyword in medical_keywords)
        
        return has_medical_keyword


    def _build_clinical_context(self, lab_data, risks, patient_info):
        parts = []
        parts.append(f"Patient: {patient_info.get('age')}yo {patient_info.get('gender')}")
        
        if lab_data:
            parts.append("Lab Data:")
            for k, v in lab_data.items():
                parts.append(f"  {k}: {v}")
        
        high_risks = {k: v for k, v in risks.items() if v.get('label') == 'high'}
        if high_risks:
            parts.append("High Risks:")
            for d, r in high_risks.items():
                parts.append(f"  {d}: {r.get('probability', 0)*100:.1f}%")
        
        return '\n'.join(parts)
