import openai
from dotenv import load_dotenv
import os

# Load the API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(message_history):
    """
    Takes a list of Message objects, formats them, and gets a response from the AI.
    """
    if not openai.api_key:
        return "ERROR: OpenAI API key is not configured. Please check your .env file."

    # The AI model expects messages in a specific dictionary format.
    formatted_messages = [
        {"role": msg.role, "content": msg.content} for msg in message_history
    ]

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",  # Using the model you requested
            messages=formatted_messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred with OpenAI API: {e}")
        return "Sorry, I encountered an error and can't respond right now."