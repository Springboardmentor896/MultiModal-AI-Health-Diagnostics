"""
AI Agent Module - MEDICAL QUESTIONS ONLY
Ultra-strict filtering with whitelist approach
"""

import os
import re
from typing import Dict, Any


def extract_parameters_with_agent(text: str) -> Dict[str, Any]:
    """Extract lab parameters using Google AI"""
    
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""Extract all lab parameters from this medical report.

Text: {text}

Format: PARAMETER: name | VALUE: number | UNIT: unit | STATUS: status | REFERENCE: range"""
            
            response = model.generate_content(prompt)
            parameters = parse_agent_response(response.text)
            
            if parameters:
                print(f"✓ Google AI extracted {len(parameters)} parameters")
                return parameters
        except Exception as e:
            print(f"⚠️ Google AI failed: {e}")
    
    return fallback_parameter_extraction(text)


def parse_agent_response(response_text: str) -> Dict[str, Any]:
    """Parse AI response"""
    parameters = {}
    
    for line in response_text.split('\n'):
        if 'PARAMETER:' in line:
            try:
                parts = line.split('|')
                param_name = parts[0].split(':')[1].strip()
                value = parts[1].split(':')[1].strip()
                unit = parts[2].split(':')[1].strip() if len(parts) > 2 else ''
                status = parts[3].split(':')[1].strip() if len(parts) > 3 else 'UNKNOWN'
                reference = parts[4].split(':')[1].strip() if len(parts) > 4 else ''
                
                parameters[param_name] = {
                    'value': value,
                    'unit': unit,
                    'status': status,
                    'reference_range': reference
                }
            except:
                continue
    
    return parameters


def fallback_parameter_extraction(text: str) -> Dict[str, Any]:
    """Regex-based fallback extraction"""
    
    parameters = {}
    patterns = {
        'Hemoglobin': r'(?:hemoglobin|hb|hgb)[:\s]*(\d+\.?\d*)',
        'WBC': r'(?:wbc|white blood cell)[:\s]*(\d+\.?\d*)',
        'Platelets': r'(?:platelet|plt)[:\s]*(\d+\.?\d*)',
        'Glucose': r'(?:glucose|sugar)[:\s]*(\d+\.?\d*)',
        'Creatinine': r'(?:creatinine)[:\s]*(\d+\.?\d*)',
        'ALT': r'(?:alt|sgpt)[:\s]*(\d+\.?\d*)',
        'AST': r'(?:ast|sgot)[:\s]*(\d+\.?\d*)',
        'Cholesterol': r'(?:cholesterol|chol)[:\s]*(\d+\.?\d*)',
        'HbA1c': r'(?:hba1c|a1c)[:\s]*(\d+\.?\d*)',
        'TSH': r'(?:tsh)[:\s]*(\d+\.?\d*)'
    }
    
    text_lower = text.lower()
    
    for param_name, pattern in patterns.items():
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            parameters[param_name] = {
                'value': str(value),
                'unit': get_default_unit(param_name),
                'status': determine_status(param_name, value),
                'reference_range': get_reference_range(param_name)
            }
    
    return parameters


def determine_status(param_name: str, value: float) -> str:
    """Determine if parameter is normal, high, or low"""
    
    ranges = {
        'Hemoglobin': (12, 16),
        'WBC': (4000, 11000),
        'Platelets': (150000, 450000),
        'Glucose': (70, 100),
        'Creatinine': (0.6, 1.3),
        'ALT': (7, 56),
        'AST': (10, 40),
        'Cholesterol': (125, 200),
        'HbA1c': (4.0, 5.6),
        'TSH': (0.4, 4.0)
    }
    
    if param_name in ranges:
        low, high = ranges[param_name]
        if value < low:
            return 'LOW'
        elif value > high:
            return 'HIGH'
        return 'NORMAL'
    
    return 'UNKNOWN'


def get_default_unit(param_name: str) -> str:
    """Get default unit for parameter"""
    
    units = {
        'Hemoglobin': 'g/dL',
        'WBC': 'cells/μL',
        'Platelets': 'cells/μL',
        'Glucose': 'mg/dL',
        'Creatinine': 'mg/dL',
        'ALT': 'U/L',
        'AST': 'U/L',
        'Cholesterol': 'mg/dL',
        'HbA1c': '%',
        'TSH': 'mIU/L'
    }
    
    return units.get(param_name, '')


def get_reference_range(param_name: str) -> str:
    """Get reference range for parameter"""
    
    ranges = {
        'Hemoglobin': '12-16 g/dL',
        'WBC': '4000-11000 cells/μL',
        'Platelets': '150000-450000 cells/μL',
        'Glucose': '70-100 mg/dL',
        'Creatinine': '0.6-1.3 mg/dL',
        'ALT': '7-56 U/L',
        'AST': '10-40 U/L',
        'Cholesterol': '125-200 mg/dL',
        'HbA1c': '4.0-5.6 %',
        'TSH': '0.4-4.0 mIU/L'
    }
    
    return ranges.get(param_name, '')


def health_advisor_agent(user_question: str, context: Dict[str, Any]) -> str:
    """
    Health advisor - MEDICAL QUESTIONS ONLY
    Uses strict whitelist filtering
    """
    
    question_lower = user_question.lower().strip()
    
    # ============================================================
    # MEDICAL WHITELIST - Question MUST have medical keywords
    # ============================================================
    
    medical_keywords = [
        # Specific lab parameters
        'hemoglobin', 'hb', 'glucose', 'sugar', 'cholesterol', 'ldl', 'hdl',
        'creatinine', 'wbc', 'rbc', 'platelet', 'hba1c', 'a1c', 'tsh',
        'alt', 'sgpt', 'ast', 'sgot', 'bilirubin', 'albumin', 'protein',
        
        # Body systems and organs
        'blood', 'heart', 'kidney', 'liver', 'lung', 'thyroid',
        
        # Medical conditions
        'anemia', 'diabetes', 'hypertension', 'pressure', 'infection',
        'disease', 'disorder', 'syndrome',
        
        # Symptoms and states
        'pain', 'fever', 'sick', 'ill', 'symptom', 'tired', 'fatigue',
        
        # Lab and medical context
        'lab', 'test', 'result', 'report', 'parameter', 'value',
        'abnormal', 'normal', 'high', 'low', 'elevated', 'decreased',
        'risk', 'level', 'count', 'range',
        
        # Healthcare
        'doctor', 'hospital', 'clinic', 'physician', 'medical',
        'health', 'treatment', 'medication', 'medicine', 'drug',
        'diagnosis', 'concern', 'worried', 'advice', 'recommend'
    ]
    
    # Check if question contains ANY medical keyword
    has_medical_keyword = any(keyword in question_lower for keyword in medical_keywords)
    
    # If NO medical keywords found -> REJECT immediately
    if not has_medical_keyword:
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

**Examples of medical questions:**
- "What does high hemoglobin mean?"
- "Is my glucose level concerning?"
- "What causes low platelets?"
- "Should I see a doctor about these results?"
- "What are symptoms of anemia?"
"""
    
    # ============================================================
    # PASSED WHITELIST - Proceed with AI response
    # ============================================================
    
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not google_key:
        return "⚠️ Error: GOOGLE_API_KEY not found in environment variables."
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Get context
        patient_info = context.get('patient_info', {})
        analysis = context.get('analysis', {})
        parameters = context.get('parameters', {})
        
        # Build prompt
        prompt = f"""You are a medical AI health advisor specializing in laboratory results.

Patient Information:
- Age: {patient_info.get('age', 'Unknown')}
- Gender: {patient_info.get('gender', 'Unknown')}

Lab Parameters:
{str(parameters)[:800]}

Analysis Summary:
{str(analysis)[:800]}

User's Medical Question: {user_question}

Provide helpful medical information and advice based on the lab results. Be specific and reference their actual lab values when relevant.
"""
        
        # Get response
        response = model.generate_content(prompt)
        answer = response.text
        
        # Add medical disclaimer
        answer += "\n\n---\n⚕️ **Medical Disclaimer:** This information is for educational purposes only. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment."
        
        return answer
        
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
