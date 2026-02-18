import json
from typing import Dict, Any, List
from pathlib import Path
import difflib  # Simple similarity

BASE_DIR = Path(__file__).parent.parent
KB_PATH = BASE_DIR / "data" / "guidelines.json"  # Curated snippets

with open(KB_PATH, 'r') as f:
    KNOWLEDGE_BASE = json.load(f)  # {"high_Glucose": "Elevated glucose may indicate... consult doctor"}

def retrieve_knowledge(findings: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve relevant guidelines by param/status similarity."""
    relevant = []
    query_terms = [f"{p}_{s}" for p, data in findings.items() 
                   for s in [data.get("status", "")] if s]
    
    for term in query_terms:
        matches = difflib.get_close_matches(term, KNOWLEDGE_BASE.keys(), n=1, cutoff=0.6)
        if matches:
            relevant.append({
                "query_term": term,
                "snippet": KNOWLEDGE_BASE[matches[0]],
                "relevance": 0.8  # Mock score
            })
    
    return relevant[:top_k]
