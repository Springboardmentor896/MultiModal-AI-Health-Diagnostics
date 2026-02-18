"""
Agent Planner: map inferred intent to a sequence of steps.
"""
def create_plan(intent: str):
    if intent == "analyze_report":
        return [
            "parse_input",
            "extract_data",
            "validate_data",
            "interpret_parameters",
            "calculate_risk",
            "context_analysis",
            "synthesize",
            "generate_recommendations",
        ]
    if intent == "ask_general_health_question":
        return ["direct_llm_response"]
    return ["request_clarification"]
