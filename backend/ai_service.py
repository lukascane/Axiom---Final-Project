from dotenv import load_dotenv
import os
from openai import OpenAI

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("ERROR: OpenAI API key not found. Check your .env file in /backend.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def get_ai_response(message_history):
    """
    Takes a list of Message objects, formats them, and gets a response from the AI.
    """
    # The AI model expects messages in a specific dictionary format.
    formatted_messages = [
        {"role": msg.role, "content": msg.content} for msg in message_history
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-4o if you prefer
            messages=formatted_messages
        )
        return completion.choices[0].message.content

    except Exception as e:
        print(f"An error occurred with OpenAI API: {e}")
        return "Sorry, I encountered an error and can't respond right now."
