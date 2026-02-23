from typing import Dict, Any, List

def plan_workflow(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Map intent to tool sequence and config."""
    plans = {
        "analyze_single_report": {
            "sequence": [
                "ingestion:parse",
                "ingestion:extract",
                "ingestion:validate",
                "models:model1",
                "models:model3",
                "models:model2",
                "rag:retrieve",
                "synthesis:findings",
                "synthesis:confidence",
                "synthesis:recommend",
                "report:generate"
            ],
            "context": {"age": params.get("age"), "gender": params.get("gender")}
        },
        "compare_reports": {
            "sequence": ["ingestion:parse"] * 2 + ["compare", "synthesis:findings", "report:generate"],
            "context": {}
        },
        "explain_parameter": {
            "sequence": ["rag:retrieve", "report:generate"],
            "context": {"param": params.get("param_name")}
        },
        "general_advice": {
            "sequence": ["rag:retrieve", "synthesis:recommend"],
            "context": {}
        }
    }
    return plans.get(intent, plans["analyze_single_report"])
