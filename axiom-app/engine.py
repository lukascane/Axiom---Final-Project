import os
import sys
from openai import OpenAI, APIStatusError
from dotenv import load_dotenv

# This line loads the variables from your .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# This is a crucial check to make sure the key was found.
if not api_key:
    print("---")
    print("ERROR: Your OPENAI_API_KEY was not found.")
    print("Please make sure you have a file named '.env' in the 'axiom-app' directory,")
    print("and make sure it contains the line: OPENAI_API_KEY='sk-yourkey'")
    print("---")
    sys.exit(1) # This stops the program if the key is missing.


# This creates the official OpenAI client with your key.
client = OpenAI(api_key=api_key)

def get_ai_chat_response(messages: list):
    """
    This function takes a list of messages (the conversation history)
    and gets a response from the OpenAI API.
    """
    # --- NEW SIMULATION LOGIC ---
    # I'm checking if the last message from the user is our special trigger phrase.
    # The last message in the list is always the user's most recent one.
    last_user_message = messages[-1]['content']
    if last_user_message == "simulate billing error":
        print("--- AI ENGINE: Simulating a billing error. ---")
        # I'll raise a specific error that my app.py knows how to handle.
        raise APIStatusError("Simulated billing error", response=None, body={"error": {"code": "insufficient_quota"}}, status_code=429)
    # --- END OF SIMULATION LOGIC ---

    print(f"--- AI ENGINE: Sending {len(messages)} messages to OpenAI. ---")
    try:
        # This is the actual call to the OpenAI API, using the gpt-3.5-turbo model.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        # We extract just the text content from the AI's full response.
        ai_message = response.choices[0].message.content.strip()
        print("--- AI ENGINE: Received response from OpenAI. ---")
        return ai_message
    except APIStatusError as e:
        # This is a more specific error check for OpenAI's responses.
        print(f"[ERROR] OpenAI API status error: {e}")
        if e.status_code == 429:
            return "API call failed due to a billing issue. Please check your plan and billing details on the OpenAI website."
        else:
            return "Sorry, the AI service returned an error. Please try again later."
    except Exception as e:
        # This is a general catch-all for other problems, like network issues.
        print(f"[ERROR] An unexpected error occurred: {e}")
        return "Sorry, I encountered an unexpected error while processing your request."