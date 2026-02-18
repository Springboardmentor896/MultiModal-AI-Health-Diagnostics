class ConversationMemory:
    def __init__(self):
        """
        Initializes an empty list to store the conversation flow.
        """
        self.history = []

    def add(self, role, message):
        """
        Adds a new interaction to the history.
        Args:
            role (str): 'user' or 'assistant' (or 'model' for Gemini).
            message (str): The actual text content of the message.
        """
        # Normalizing role names to ensure compatibility with Gemini's format
        role_label = "user" if role.lower() == "user" else "model"
        self.history.append({"role": role_label, "parts": [message]})

    def get_history(self):
        """
        Returns the full conversation history.
        """
        return self.history

    def get_formatted_history_text(self):
        """
        Returns history as a single string for use in text-based prompts 
        like the one in intent_inference.py.
        """
        formatted_text = ""
        for entry in self.history:
            speaker = "User" if entry["role"] == "user" else "Assistant"
            text = entry["parts"][0]
            formatted_text += f"{speaker}: {text}\n"
        return formatted_text

    def clear(self):
        """
        Resets the memory for a new session.
        """
        self.history = []