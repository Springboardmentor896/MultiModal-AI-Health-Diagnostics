import subprocess
import json
import time
import os
import re

def clean_ollama_output(text):
    """Clean Ollama output while preserving readable text"""
    if not text:
        return ""
    
    # Remove ANSI escape sequences (progress bars, colors)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # Remove Unicode progress characters and symbols
    progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏', '▕', '█', '▏']
    for char in progress_chars:
        text = text.replace(char, '')
    
    # Remove common Ollama status words that appear in output
    noise_patterns = [
        r'pulling manifest.*?\n',
        r'pulling \w+:.*?%.*?\n',
        r'verifying sha256 digest.*?\n',
        r'writing manifest.*?\n',
        r'success.*?\n'
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up whitespace and filter meaningful lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_lines = []
    
    for line in lines:
        # Skip lines that are clearly progress/status messages
        if not re.match(r'^[\d\s%▕█▏]*$', line) and 'pulling' not in line.lower() and 'verifying' not in line.lower():
            clean_lines.append(line)
    
    return '\n'.join(clean_lines)

def ollama_synthesize_findings(classification_results, risk_assessment, model2_patterns=None, user_context=None, timeout=30):
    """Generate clinical summary using Ollama with fallback"""
    
    # Build prompt
    abnormal_params = [f"- {k}: {v['value']} ({v['status']})" for k, v in classification_results.items() if v.get('status') != 'Normal']
    risks = risk_assessment['identified_risks'][:3]
    
    prompt = f"""You are a medical AI. Create a clinical summary in bullet point format.

Patient: Age: {user_context.get('age', 'Unknown')}, Gender: {user_context.get('gender', 'Unknown')}
Risk Level: {risk_assessment['risk_level']} (score {risk_assessment['risk_score']})

Abnormal Parameters:
{chr(10).join(abnormal_params)}

Key Risks:
{chr(10).join([f"- {risk}" for risk in risks])}

Format your response as bullet points starting with:
• Patient Demographics: 
• Risk Assessment:
• Laboratory Findings:
• Clinical Concerns:
• Overall Assessment:"""

    try:
        # Set environment variables for UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        
        # FIXED: Use 'ollama run' instead of 'ollama pull'
        result = subprocess.run(
            ['ollama', 'run', 'tinyllama'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout*2,
            env=env
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Clean the output properly
            clean_output = clean_ollama_output(result.stdout)
            return clean_output if clean_output else get_fallback_summary(classification_results, risk_assessment)
        else:
            print(f"Ollama stderr: {result.stderr}")
            return get_fallback_summary(classification_results, risk_assessment)
            
    except Exception as e:
        print(f"Ollama call failed: {e}")
        return get_fallback_summary(classification_results, risk_assessment)

def ollama_generate_recommendations(clinical_summary, abnormal_params, risk_level, user_context=None, timeout=30):
    """Generate recommendations using Ollama with fallback"""
    
    prompt = f"""You are a health AI assistant. Give 6 specific recommendations.

Patient: Age: {user_context.get('age', 'Unknown')}, Gender: {user_context.get('gender', 'Unknown')}, Activity: {user_context.get('activity_level', 'moderate')}
Risk Level: {risk_level}
Summary: {clinical_summary}
Abnormal Parameters: {', '.join(abnormal_params)}

Provide 6 health recommendations. Format each as:
[CATEGORY] recommendation text

Categories: DIET, LIFESTYLE, FOLLOW_UP, PRECAUTIONS

Example:
[DIET] Reduce sodium intake to less than 2g per day
[FOLLOW_UP] Schedule cardiology consultation within 2 weeks"""

    try:
        # Set environment variables for UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        
        # FIXED: Use 'ollama run' instead of 'ollama pull'
        result = subprocess.run(
            ['ollama', 'run', 'tinyllama'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout*2,
            env=env
        )
        
        if result.returncode == 0 and result.stdout.strip():
            clean_output = clean_ollama_output(result.stdout)
            return parse_recommendations(clean_output)
        else:
            print(f"Ollama stderr: {result.stderr}")
            return get_fallback_recommendations(risk_level, abnormal_params, user_context)
            
    except Exception as e:
        print(f"Ollama call failed: {e}")
        return get_fallback_recommendations(risk_level, abnormal_params, user_context)

def parse_recommendations(ollama_output):
    """Parse Ollama output into structured recommendations"""
    recommendations = []
    
    try:
        lines = ollama_output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and '[' in line and ']' in line:
                try:
                    # Find category in brackets
                    start_idx = line.find('[')
                    end_idx = line.find(']')
                    
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        category = line[start_idx + 1:end_idx].strip().lower()
                        text = line[end_idx + 1:].strip()
                        
                        if category and text and len(text) > 10:  # Ensure meaningful text
                            recommendations.append({
                                "category": category,
                                "text": text
                            })
                except Exception:
                    continue
        
        # If we don't have enough recommendations, fill with fallback
        if len(recommendations) < 3:
            return get_fallback_recommendations("HIGH", [], {})
            
        return recommendations[:6]  # Return max 6
        
    except Exception as e:
        print(f"Error parsing recommendations: {e}")
        return get_fallback_recommendations("HIGH", [], {})

def get_fallback_summary(classification_results, risk_assessment):
    """Generate fallback summary in bullet point format when Ollama fails"""
    
    # Get patient demographics
    demo = risk_assessment.get('demographic_context', {})
    age = demo.get('age', 'unknown')
    gender = demo.get('gender', 'unknown')
    
    # Get abnormal parameters
    abnormal_params = [(k, v['value'], v['status']) for k, v in classification_results.items() 
                      if v.get('status') != 'Normal']
    
    # Build bullet point summary
    summary_lines = [
        f"• Patient Demographics: {age}-year-old {gender}",
        f"• Risk Assessment: {risk_assessment['risk_level']} (Score: {risk_assessment['risk_score']}/10)"
    ]
    
    if abnormal_params:
        summary_lines.append("• Laboratory Findings:")
        for param, value, status in abnormal_params:
            param_display = param.replace('_', ' ').title()
            summary_lines.append(f"  - {param_display}: {value} ({status})")
    
    if risk_assessment['identified_risks']:
        summary_lines.append("• Clinical Concerns:")
        for risk in risk_assessment['identified_risks'][:3]:
            summary_lines.append(f"  - {risk}")
    
    summary_lines.append("• Overall Assessment: Immediate medical consultation required for abnormal parameters")
    
    return "\n".join(summary_lines)

def get_fallback_recommendations(risk_level, abnormal_params, user_context):
    """Provide fallback recommendations when Ollama fails"""
    
    age = user_context.get('age', 65) if user_context else 65
    
    base_recommendations = [
        {"category": "follow_up", "text": "Schedule immediate nephrology and hepatology consultation for elevated parameters"},
        {"category": "diet", "text": "Adopt kidney and liver-friendly diet with reduced protein (0.8g/kg) and sodium (2g/day)"},
        {"category": "lifestyle", "text": "Maintain gentle daily walks (15-20 minutes) avoiding overexertion"},
        {"category": "precautions", "text": "Monitor for symptoms: swelling, dark urine, yellowing skin/eyes, fatigue"},
        {"category": "diet", "text": "Complete alcohol avoidance and limit over-the-counter medications (NSAIDs)"},
        {"category": "lifestyle", "text": "Ensure 7-8 hours quality sleep and practice stress reduction techniques"}
    ]
    
    # Customize based on risk level
    if risk_level == "HIGH":
        base_recommendations[0]["text"] = "Arrange urgent clinical review due to elevated creatinine, bilirubin, and AST levels"
        base_recommendations.insert(1, {"category": "precautions", "text": "Have emergency contact information readily available"})
    
    # Customize for elderly patients
    if age >= 65:
        base_recommendations[2]["text"] = "Maintain gentle daily walks and light stretching exercises appropriate for seniors"
        base_recommendations.append({"category": "follow_up", "text": "Consider comprehensive medication review to avoid drug interactions"})
    
    return base_recommendations[:6]