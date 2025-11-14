import os
from openai import OpenAI  # <-- Import the new client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. Initialize the new OpenAI client ---
# This is the new, correct way to set the API key
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

if not os.getenv('OPENAI_API_KEY'):
    print("Warning: OPENAI_API_KEY is not set.")

def get_ai_response(messages_history):
    """
    Takes a list of ChatMessage objects and returns a string response from the AI.
    """
    
    # 1. Format messages for the OpenAI API
    openai_messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    for msg in messages_history:
        openai_messages.append({"role": msg.role, "content": msg.content})

    # 2. Call OpenAI using the new client syntax
    try:
        # --- This is the new, correct syntax ---
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # <-- CHANGED FROM gpt-3.5-turbo
            messages=openai_messages
        )
        ai_response_content = completion.choices[0].message.content
        # --- End of new syntax ---
        
        return ai_response_content
        
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return "Sorry, I encountered an error while processing your request."