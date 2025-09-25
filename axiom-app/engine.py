import time
import random
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# This loads your API key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# This is a new check to make sure the API key was actually found.
# If it's not found, the program will stop and print a helpful message.
if not api_key:
    print("---")
    print("ERROR: Your OPENAI_API_KEY was not found.")
    print("Please make sure you have a file named '.env' in the 'axiom-app' directory,")
    print("and make sure it contains the line: OPENAI_API_KEY='sk-yourkey'")
    print("---")
    sys.exit(1)


client = OpenAI(api_key=api_key)

def get_ai_chat_response(messages: list):
    """
    This function takes a conversation history and gets a response from OpenAI.
    """
    print(f"--- AI ENGINE: Sending {len(messages)} messages to OpenAI. ---")

    try:
        # This is the actual call to the OpenAI API.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        # We extract the text content from the AI's response.
        ai_message = response.choices[0].message.content.strip()
        print("--- AI ENGINE: Received response from OpenAI. ---")
        return ai_message
    except Exception as e:
        # If anything goes wrong, we return a clear error message.
        print(f"[ERROR] OpenAI API call failed: {e}")
        return "Sorry, I encountered an error while processing your request."

