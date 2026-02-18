def create_plan(intent):
   
    if intent == "analyze_report":
        return [
            "parse_input",            
            "extract_data",           
            "validate_data",          
            "context_analysis",       
            "interpret_parameters",    
            "calculate_risk",          
            "query_knowledge_base",    
            "synthesize",              
            "generate_recommendations" 
        ]
    
    elif intent == "ask_general_health_question":
        return [
            "query_knowledge_base",    
            "direct_llm_response"      
        ]
    
    elif intent == "request_clarification":
        return [
            "fetch_memory_context",    
            "provide_clarification"
        ]
    
    return ["generic_assistance"]