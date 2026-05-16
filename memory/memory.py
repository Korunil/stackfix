from langchain_core.chat_history import InMemoryChatMessageHistory

class ChatMemory:
    def __init__(self, k=3, max_chars_per_msg=1000):
        # Reduced default k to 3; debugging turns are heavy
        self.k = k
        self.max_chars = max_chars_per_msg
        self.store = InMemoryChatMessageHistory()

    def add(self, user, assistant):
        self.store.add_user_message(user)
        self.store.add_ai_message(assistant)

    def get_messages(self):
        # Maintains the last k rounds (user + ai)
        return self.store.messages[-self.k*2:]

    def format(self):
        msgs = self.get_messages()
        formatted_turns = []
        
        for m in msgs:
            # Map LangChain types to your prompt roles
            role = "USER" if m.type == "human" else "STACKFIX"
            
            # Truncate content to prevent history from eating the context window
            content = m.content
            if len(content) > self.max_chars:
                content = content[:self.max_chars]
                last_newline = content.rfind("\n")

                if last_newline > 200:
                    content = content[:last_newline]

                content +=  "\n... [truncated]"
            
            formatted_turns.append(f"{role}: {content}")
        
        return "\n".join(formatted_turns)