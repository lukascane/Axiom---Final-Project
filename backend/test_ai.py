from ai_service import get_ai_response

# Simulate a short conversation
class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

messages = [
    Message("user", "Hello, who are you?")
]

print(get_ai_response(messages))
