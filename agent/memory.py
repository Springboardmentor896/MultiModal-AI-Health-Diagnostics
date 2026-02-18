class ConversationMemory:
    def __init__(self):
        self.history = []

    def add(self, role, message):
        role_label = "user" if role.lower() == "user" else "model"
        self.history.append({"role": role_label, "parts": [message]})

    def get_history(self):
        return self.history

    def get_formatted_history_text(self):
        formatted_text = ""
        for entry in self.history:
            speaker = "User" if entry["role"] == "user" else "Assistant"
            text = entry["parts"][0]
            formatted_text += f"{speaker}: {text}\n"
        return formatted_text

    def clear(self):
        self.history = []