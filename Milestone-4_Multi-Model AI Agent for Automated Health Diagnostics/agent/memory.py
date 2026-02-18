"""
Conversation memory for context and intent inference.
"""
class ConversationMemory:
    def __init__(self):
        self.history = []

    def add(self, role: str, message: str):
        self.history.append({"role": role, "message": message})

    def get_history(self):
        return self.history
