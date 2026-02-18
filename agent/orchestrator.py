from agent.intent_inference import infer_intent
from agent.planner import create_plan
from ingestion.parser import parse_input
from ingestion.extractor import extract_parameters
from ingestion.validator import validate_data
from models.model1 import interpret
from models.model2 import calculate_risk
from models.model3 import contextual_adjustment
from synthesis.synthesizer import synthesize
from synthesis.confidence import calculate_confidence
from synthesis.recommender import generate_recommendations, generate_general_health_response
from report.generator import generate_full_report
from rag.knowledge_base import retrieve_guideline

def run_agent(user_input, file=None, age=None, gender=None, memory=None):
    intent = infer_intent(user_input, memory.get_history())
    plan = create_plan(intent)

    if intent == "analyze_report":
        if file is None:
            return "Please upload a blood report for analysis.", 0
    
        file_ext = file.name.split('.')[-1].lower() 
        if file_ext in ["jpg", "jpeg", "png"]:
            file_type = "image"
        else:
            file_type = file_ext
    
        text = parse_input(file, file_type)
        
        data = extract_parameters(text)
        data = validate_data(data)

        if not data:
            return f"No valid parameters detected in the {file_ext.upper()} report.", 0
            
        m1 = interpret(data)

        rag_context = []
        for param, details in m1.items():
            if details['status'] != "Normal":
                key = f"{details['status']} {param.replace('_', ' ').title()}"
                guideline = retrieve_guideline(key)
                if guideline:
                    rag_context.append(f"{param.upper()}: {guideline}")
                    
        risk = calculate_risk(data, age)
        context_flags = contextual_adjustment(data, age, gender)

        summary = synthesize(m1, risk, context_flags)
        confidence = calculate_confidence(data)
        recommendations = generate_recommendations(summary, rag_context)
        
        report = generate_full_report(
            m1,
            summary,
            recommendations,
            confidence
        )

        return report, confidence

    elif intent == "ask_general_health_question":
        response = generate_general_health_response(user_input)
        return response, 100

    else:
        return "Could you please clarify your request? I can help analyze blood reports or answer general health questions.", 0


    if __name__ == "__main__":
        from agent.memory import ConversationMemory
        
        test_memory = ConversationMemory()
        test_input = "Can you analyze this report ?"
        
        print("--- STARTING LOCAL AGENT TEST ---")
        report, confidence = run_agent(test_input, file=None, memory=test_memory)
        
        print(f"Intent Result: {report}")
        print(f"Confidence: {confidence}%")
        print("--- TEST COMPLETE ---")