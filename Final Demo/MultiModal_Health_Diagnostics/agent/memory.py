from typing import Dict, Any, Optional
from datetime import datetime

class Memory:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> data

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or init session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "patient": {"age": None, "gender": None, "name": None},
                "last_analysis": None,
                "timestamp": datetime.now().isoformat()
            }
        return self.sessions[session_id]

    def save_analysis(self, session_id: str, analysis: Dict[str, Any]):
        """Store latest results."""
        session = self.get_session(session_id)
        session["history"].append(session["last_analysis"])
        session["last_analysis"] = analysis
        session["timestamp"] = datetime.now().isoformat()

memory = Memory()  # Global instance
