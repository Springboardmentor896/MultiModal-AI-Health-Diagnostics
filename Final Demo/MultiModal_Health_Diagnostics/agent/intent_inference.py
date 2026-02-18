from typing import Dict, Any
import os

# Try to import groq
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    print("⚠️ Groq not installed. Using rule-based intent. Run: pip install groq")

def infer_intent_with_llm(query: str, api_key: str) -> Dict[str, Any]:
    """Use Groq LLM to infer intent (fast & free)."""
    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""Analyze this health query and return ONLY the intent name (one word).

Query: "{query}"

Intents:
- analyze_report: User wants blood report analysis
- compare_reports: Compare multiple reports
- explain_parameter: Explain specific parameter
- get_recommendations: Health recommendations

Intent:"""

        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast Groq model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        
        intent = response.choices[0].message.content.strip().lower()
        
        # Validate
        valid = ["analyze_report", "compare_reports", "explain_parameter", "get_recommendations"]
        if intent not in valid:
            intent = "analyze_report"
        
        return {
            "intent": intent,
            "confidence": 0.95,
            "query": query,
            "method": "groq_llm",
            "params": {}
        }
    except Exception as e:
        print(f"⚠️ Groq API failed: {e}. Using rule-based fallback.")
        return infer_intent_rule_based(query)

def infer_intent_rule_based(query: str) -> Dict[str, Any]:
    """Fallback rule-based intent."""
    query_lower = query.lower()
    
    if any(w in query_lower for w in ['analyze', 'check', 'report', 'review']):
        intent = "analyze_report"
        confidence = 0.85
    elif any(w in query_lower for w in ['compare', 'vs', 'difference']):
        intent = "compare_reports"
        confidence = 0.8
    elif any(w in query_lower for w in ['explain', 'what', 'why', 'mean']):
        intent = "explain_parameter"
        confidence = 0.75
    elif any(w in query_lower for w in ['recommend', 'suggest', 'advice']):
        intent = "get_recommendations"
        confidence = 0.8
    else:
        intent = "analyze_report"
        confidence = 0.7
    
    return {
        "intent": intent,
        "confidence": confidence,
        "query": query,
        "method": "rule_based",
        "params": {}
    }

def infer_intent(query: str, api_key: str = None) -> Dict[str, Any]:
    """Main: tries Groq LLM, falls back to rules."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    
    if HAS_GROQ and api_key:
        return infer_intent_with_llm(query, api_key)
    else:
        return infer_intent_rule_based(query)
